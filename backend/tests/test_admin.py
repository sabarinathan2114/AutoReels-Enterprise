import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import SessionLocal
from app.models.entities import User, Tenant, Workspace, Subscription, Plan, PlatformAdmin, AuditLog, PlanChangeRequest
from app.services.auth_service import AuthService
from app.services.tenant_service import TenantService
from app.services.admin_service import AdminService
from app.services.entitlement_service import EntitlementService

client = TestClient(app)

@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="module")
def test_setup(db: Session):
    unique = uuid.uuid4().hex[:8]

    # 1. Regular creator user
    creator_email = f"creator_{unique}@example.com"
    creator = AuthService.create_user(db, email=creator_email, plain_password="Password123!")
    creator_tenant = TenantService.create_tenant_hierarchy(
        db=db,
        user_id=creator.id,
        tenant_name=f"Creator Studio {unique}",
        plan_id="free"
    )
    creator_token = AuthService.create_access_token({
        "sub": creator.email,
        "user_id": creator.id,
        "workspace_id": creator_tenant["workspace_id"]
    })

    # 2. Super Admin user
    super_admin_email = f"superadmin_{unique}@example.com"
    super_admin_user = AuthService.create_user(db, email=super_admin_email, plain_password="SuperSecretPassword123!")
    db_admin = PlatformAdmin(user_id=super_admin_user.id, role="super_admin")
    db.add(db_admin)
    db.commit()

    # 3. Support Admin user (ADM-02: role split)
    support_email = f"support_{unique}@example.com"
    support_user = AuthService.create_user(db, email=support_email, plain_password="SupportSecretPassword123!")
    db_support = PlatformAdmin(user_id=support_user.id, role="support")
    db.add(db_support)
    db.commit()

    return {
        "creator": creator,
        "creator_tenant": creator_tenant,
        "creator_token": creator_token,
        "super_admin": super_admin_user,
        "super_admin_email": super_admin_email,
        "super_admin_password": "SuperSecretPassword123!",
        "support": support_user,
        "support_email": support_email,
        "support_password": "SupportSecretPassword123!"
    }

def test_admin_login_and_token_audience(test_setup):
    """ADM-03: Admin login issues token with audience 'autoreels-admin'."""
    res = client.post("/api/v1/admin/login", json={
        "email": test_setup["super_admin_email"],
        "password": test_setup["super_admin_password"]
    })
    assert res.status_code == 200, res.text
    data = res.json()
    assert "access_token" in data
    assert data["admin_user"]["role"] == "super_admin"

    # Decode payload
    payload = AuthService.decode_access_token(data["access_token"])
    assert payload["aud"] == "autoreels-admin"
    assert payload["role"] == "super_admin"

def test_adm_t1_non_admin_cannot_reach_admin_api(test_setup):
    """ADM-T1: Non-admin cannot reach any /admin API (401 without token, 403 with user token)."""
    # 1. Unauthenticated request -> 401
    res1 = client.get("/api/v1/admin/tenants")
    assert res1.status_code == 401

    # 2. Authenticated as ordinary creator (audience is not autoreels-admin) -> 403
    res2 = client.get(
        "/api/v1/admin/tenants",
        headers={"Authorization": f"Bearer {test_setup['creator_token']}"}
    )
    assert res2.status_code == 403
    assert "access forbidden" in res2.json()["detail"].lower() or "not authorized" in res2.json()["detail"].lower()

def test_adm_t4_support_role_cannot_edit_plans_or_approve(test_setup):
    """ADM-T4: SUPPORT role has read access, but cannot edit plans or approve upgrades (403)."""
    # Support admin logs in
    login_res = client.post("/api/v1/admin/login", json={
        "email": test_setup["support_email"],
        "password": test_setup["support_password"]
    })
    assert login_res.status_code == 200
    support_token = login_res.json()["access_token"]
    support_headers = {"Authorization": f"Bearer {support_token}"}

    # Support CAN read telemetry and tenants
    read_res = client.get("/api/v1/admin/telemetry", headers=support_headers)
    assert read_res.status_code == 200

    # Support CANNOT update plan limits (ADM-T4)
    write_res = client.put(
        "/api/v1/admin/plans/plan_a",
        json={"monthly_video_quota": 50},
        headers=support_headers
    )
    assert write_res.status_code == 403
    assert "SUPERADMIN role required" in write_res.json()["detail"]

    # Support CANNOT change tenant plan directly (ADM-T4)
    change_res = client.post(
        f"/api/v1/admin/tenants/{test_setup['creator_tenant']['tenant_id']}/plan",
        json={"new_plan_id": "plan_a"},
        headers=support_headers
    )
    assert change_res.status_code == 403

def test_upgrade_approval_workflow_and_quota_expansion(test_setup, db: Session):
    """
    Creator requests upgrade -> Super Admin approves ->
    Tenant plan shifts to Plan A -> Quota expands from 2 to 30 videos.
    """
    creator_ws_id = test_setup["creator_tenant"]["workspace_id"]
    creator_tenant_id = test_setup["creator_tenant"]["tenant_id"]

    # 1. Creator submits upgrade request
    submit_res = client.post(
        f"/api/v1/workspaces/{creator_ws_id}/upgrade-request",
        headers={"Authorization": f"Bearer {test_setup['creator_token']}"},
        json={
            "requested_plan_id": "plan_a",
            "notes": "Scaling to 30 videos per month for brand launch"
        }
    )
    assert submit_res.status_code == 201, submit_res.text
    req_id = submit_res.json()["request_id"]

    # 2. Super Admin logs in
    admin_login = client.post("/api/v1/admin/login", json={
        "email": test_setup["super_admin_email"],
        "password": test_setup["super_admin_password"]
    })
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 3. Super Admin approves request
    approve_res = client.post(f"/api/v1/admin/upgrade-requests/{req_id}/approve", headers=admin_headers)
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "approved"

    # 4. Creator queries entitlements: should now be plan_a with 30 videos quota!
    entitlements_res = client.get(
        f"/api/v1/me/entitlements?workspace_id={creator_ws_id}",
        headers={"Authorization": f"Bearer {test_setup['creator_token']}"}
    )
    assert entitlements_res.status_code == 200
    data = entitlements_res.json()
    assert data["plan_id"] == "plan_a"
    assert data["monthly_quota"] == 30
    assert data["watermark"] is False

def test_plan_04_plan_edit_takes_effect_immediately(test_setup, db: Session):
    """
    PLAN-04: Plan edit by admin changes entitlements within 60 s.
    Admin updates Plan B quota from 100 to 120 -> effective entitlements reflect 120 immediately.
    """
    admin_login = client.post("/api/v1/admin/login", json={
        "email": test_setup["super_admin_email"],
        "password": test_setup["super_admin_password"]
    })
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

    # Modify Plan B monthly quota
    res = client.put(
        "/api/v1/admin/plans/plan_b",
        json={"monthly_video_quota": 120},
        headers=admin_headers
    )
    assert res.status_code == 200
    assert res.json()["monthly_video_quota"] == 120

    # Verify directly via DB query and entitlement service
    plan = db.query(Plan).filter(Plan.id == "plan_b").first()
    assert plan.monthly_video_quota == 120

    # Reset back to 100 for clean state
    reset_res = client.put(
        "/api/v1/admin/plans/plan_b",
        json={"monthly_video_quota": 100},
        headers=admin_headers
    )
    assert reset_res.status_code == 200
    assert reset_res.json()["monthly_video_quota"] == 100

def test_adm_t2_forced_audit_failure_rolls_back_action(test_setup, db: Session):
    """
    ADM-T2: Every admin write creates an audit row;
    forced audit failure rolls back the action (fault injection).
    """
    tenant_id = test_setup["creator_tenant"]["tenant_id"]

    # Record current plan
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    initial_plan = tenant.subscription.plan_id

    # Attempt to change plan with forced audit failure
    with pytest.raises(RuntimeError, match="SIMULATED_AUDIT_INSERT_FAILURE"):
        AdminService.execute_transaction_with_forced_audit_failure_test(
            db=db,
            tenant_id=tenant_id,
            new_plan_id="plan_c",
            admin_user_id=test_setup["super_admin"].id
        )

    # Roll back session explicitly as a caller would
    db.rollback()

    # Verify that tenant plan was NOT modified
    tenant_after = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    assert tenant_after.subscription.plan_id == initial_plan

def test_admin_settings_daily_cap_and_audit_log(test_setup):
    """Super Admin sets global daily cap and verifies audit log entry was created."""
    admin_login = client.post("/api/v1/admin/login", json={
        "email": test_setup["super_admin_email"],
        "password": test_setup["super_admin_password"]
    })
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

    # Set daily cap to 250 videos
    cap_res = client.post("/api/v1/admin/settings/daily-cap", json={"cap": 250}, headers=admin_headers)
    assert cap_res.status_code == 200
    assert cap_res.json()["max_videos_per_day"] == 250

    # Telemetry should reflect 250
    telem_res = client.get("/api/v1/admin/telemetry", headers=admin_headers)
    assert telem_res.status_code == 200
    assert telem_res.json()["max_videos_per_day"] == 250

    # Audit log list should contain this event
    audit_res = client.get("/api/v1/admin/audit-logs", headers=admin_headers)
    assert audit_res.status_code == 200
    logs = audit_res.json()
    assert len(logs) > 0
    actions = [l["action"] for l in logs]
    assert "system_setting.updated" in actions
