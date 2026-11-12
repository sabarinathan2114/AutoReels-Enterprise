import uuid
import concurrent.futures
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.entities import User, Workspace, PlanChangeRequest
from app.services.auth_service import AuthService
from app.services.tenant_service import TenantService
from app.services.entitlement_service import EntitlementService

client = TestClient(app)

@pytest.fixture
def test_workspace():
    """Provisions a clean user and workspace on the Free tier."""
    db = SessionLocal()
    unique_email = f"entitle_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        email=unique_email,
        hashed_password=AuthService.hash_password("Pass123!"),
        full_name="Entitlement Tester",
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    tenant_data = TenantService.create_tenant_hierarchy(
        db=db,
        user_id=user.id,
        tenant_name="Entitlements Studio",
        plan_id="free"
    )
    ws_id = tenant_data["workspace_id"]
    db.close()
    return ws_id

def test_get_effective_entitlements(test_workspace):
    """Verifies that GET /api/v1/me/entitlements returns complete plan entitlements."""
    response = client.get(f"/api/v1/me/entitlements?workspace_id={test_workspace}")
    assert response.status_code == 200
    data = response.json()

    assert data["workspace_id"] == test_workspace
    assert data["plan_id"] == "free"
    assert data["monthly_quota"] == 2
    assert data["used_this_period"] == 0
    assert data["remaining_quota"] == 2
    assert data["watermark"] is True
    assert data["resolution"] == "720x1280"
    assert "resets_at" in data

def test_free_user_calling_publish_gets_403_feature_locked(test_workspace):
    """
    Spec Acceptance: Free user calling publish/schedule/channel APIs directly
    gets 403 FEATURE_LOCKED.
    """
    payload = {
        "account_ids": ["ch_youtube_1"],
        "video_path": "storage/output/test_reel_output.mp4",
        "title": "My Reel",
        "description": "Test description",
        "tags": ["shorts"],
        "workspace_id": test_workspace
    }
    response = client.post("/api/social/publish", json=payload)
    assert response.status_code == 403
    error_data = response.json()["detail"]
    assert error_data["error"] == "FEATURE_LOCKED"
    assert "social_publishing" in error_data["feature"]

def test_atomic_quota_concurrency_race_condition(test_workspace):
    """
    Spec Acceptance: 20-50 parallel requests with 2 videos left create exactly 2 jobs/consumptions;
    all remaining requests get 429 MONTHLY_QUOTA_EXCEEDED.
    """
    def attempt_consumption():
        db = SessionLocal()
        try:
            return EntitlementService.consume_video_quota(db, test_workspace)
        finally:
            db.close()

    successes = 0
    failures = 0

    # Fire 20 parallel threads concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(attempt_consumption) for _ in range(20)]
        for f in concurrent.futures.as_completed(futures):
            try:
                res = f.result()
                if res.get("status") == "quota_consumed":
                    successes += 1
            except Exception as ex:
                if "MONTHLY_QUOTA_EXCEEDED" in str(ex):
                    failures += 1

    # Exactly 2 succeed, exactly 18 fail!
    assert successes == 2
    assert failures == 18

    # Verify final usage counter in database is 2
    db = SessionLocal()
    try:
        final_entitlements = EntitlementService.get_effective_entitlements(db, test_workspace, use_cache=False)
        assert final_entitlements["used_this_period"] == 2
        assert final_entitlements["remaining_quota"] == 0
        assert final_entitlements["is_quota_exhausted"] is True
    finally:
        db.close()

def test_upgrade_request_submission(test_workspace):
    """Verifies that user can submit upgrade request to Plan A or B."""
    payload = {
        "requested_plan_id": "plan_a",
        "notes": "Need 30 videos per month for creator channel."
    }
    response = client.post(f"/api/v1/workspaces/{test_workspace}/upgrade-request", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert data["requested_plan_id"] == "plan_a"
    assert data["plan_name"] == "Plan A (Creator)"
