import pytest
import uuid
from app.database import SessionLocal
from app.models.entities import User, Asset, VideoProject
from app.services.tenant_service import TenantService
from app.services.auth_service import AuthService

@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()

def test_two_tenant_isolation(db):
    """
    Acceptance Criteria for Phase 2:
    Two-tenant isolation tests pass (Tenant A can never read Tenant B, and vice versa).
    """
    # 1. Create User A and Tenant A
    user_a = User(
        email=f"user_a_{uuid.uuid4().hex[:6]}@example.com",
        hashed_password=AuthService.hash_password("Pass123!"),
        full_name="Creator Alpha",
        is_verified=True
    )
    db.add(user_a)
    db.commit()
    db.refresh(user_a)

    tenant_a_data = TenantService.create_tenant_hierarchy(
        db=db,
        user_id=user_a.id,
        tenant_name="Alpha Studios",
        plan_id="free"
    )
    ws_a_id = tenant_a_data["workspace_id"]

    # 2. Create User B and Tenant B
    user_b = User(
        email=f"user_b_{uuid.uuid4().hex[:6]}@example.com",
        hashed_password=AuthService.hash_password("Pass123!"),
        full_name="Creator Beta",
        is_verified=True
    )
    db.add(user_b)
    db.commit()
    db.refresh(user_b)

    tenant_b_data = TenantService.create_tenant_hierarchy(
        db=db,
        user_id=user_b.id,
        tenant_name="Beta Studios",
        plan_id="free"
    )
    ws_b_id = tenant_b_data["workspace_id"]

    # Verify workspace IDs are distinct
    assert ws_a_id != ws_b_id

    # 3. Provision assets and projects in Workspace A
    asset_a = Asset(
        workspace_id=ws_a_id,
        asset_type="image",
        storage_key="images/alpha_scene_1.jpg",
        url="http://localhost:8000/storage/images/alpha_scene_1.jpg",
        size_bytes=55000
    )
    project_a = VideoProject(
        workspace_id=ws_a_id,
        user_id=user_a.id,
        title="Alpha Top Secret Video",
        script_text="Alpha secret script content"
    )
    db.add_all([asset_a, project_a])
    db.commit()

    # 4. Provision assets and projects in Workspace B
    asset_b = Asset(
        workspace_id=ws_b_id,
        asset_type="video",
        storage_key="output/beta_reel.mp4",
        url="http://localhost:8000/storage/output/beta_reel.mp4",
        size_bytes=102400
    )
    project_b = VideoProject(
        workspace_id=ws_b_id,
        user_id=user_b.id,
        title="Beta Public Reel",
        script_text="Beta public script content"
    )
    db.add_all([asset_b, project_b])
    db.commit()

    # 5. TEST CROSS-TENANT ISOLATION: Workspace B can NEVER see Workspace A's assets
    scoped_assets_b = TenantService.get_scoped_assets(db, ws_b_id)
    asset_b_ids = [a.id for a in scoped_assets_b]
    assert asset_b.id in asset_b_ids
    assert asset_a.id not in asset_b_ids

    # 6. TEST CROSS-TENANT ISOLATION: Workspace B can NEVER see Workspace A's projects
    scoped_projects_b = TenantService.get_scoped_projects(db, ws_b_id)
    project_b_ids = [p.id for p in scoped_projects_b]
    assert project_b.id in project_b_ids
    assert project_a.id not in project_b_ids

    # 7. TEST ACCESS VERIFICATION: User B cannot access Workspace A
    assert TenantService.verify_workspace_access(db, user_b.id, ws_a_id) is False
    assert TenantService.verify_workspace_access(db, user_a.id, ws_a_id) is True

    # 8. TEST QUOTA ISOLATION: Workspace A increments quota, Workspace B remains at 0
    TenantService.increment_quota_usage(db, ws_a_id, metric="videos_rendered", amount=2)
    quota_a = TenantService.get_current_period_quota_usage(db, ws_a_id, metric="videos_rendered")
    quota_b = TenantService.get_current_period_quota_usage(db, ws_b_id, metric="videos_rendered")

    assert quota_a >= 2
    assert quota_b == 0
