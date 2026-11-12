import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.entities import Tenant, Workspace, Membership, Subscription

client = TestClient(app)

def test_signup_provisions_tenant_and_free_plan():
    """
    Spec Acceptance: On signup/registration, create in ONE atomic transaction:
    user, tenant, default workspace, OWNER membership, subscription on FREE tier.
    """
    unique_email = f"creator_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "email": unique_email,
        "password": "SecurePassword123!",
        "full_name": "Test Studio Creator"
    }
    
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    user_info = data["user"]
    assert user_info["email"] == unique_email
    assert user_info["plan_id"] == "free"
    assert user_info["workspace_id"] is not None
    workspace_id = user_info["workspace_id"]
    
    # Verify in database
    db = SessionLocal()
    try:
        ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        assert ws is not None
        assert ws.tenant_id is not None
        
        # Verify tenant
        tenant = db.query(Tenant).filter(Tenant.id == ws.tenant_id).first()
        assert tenant is not None
        
        # Verify OWNER membership
        membership = db.query(Membership).filter(
            Membership.workspace_id == workspace_id,
            Membership.user_id == user_info["id"]
        ).first()
        assert membership is not None
        assert membership.role == "OWNER"
        
        # Verify FREE subscription
        sub = db.query(Subscription).filter(Subscription.tenant_id == tenant.id).first()
        assert sub is not None
        assert sub.plan_id == "free"
        assert sub.status == "active"
    finally:
        db.close()

def test_login_returns_tenant_workspace_and_plan():
    unique_email = f"creator_{uuid.uuid4().hex[:8]}@example.com"
    reg_payload = {
        "email": unique_email,
        "password": "SecurePassword123!",
        "full_name": "Login Studio Creator"
    }
    reg_res = client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code == 200
    orig_ws_id = reg_res.json()["user"]["workspace_id"]
    
    # Now login
    login_payload = {
        "email": unique_email,
        "password": "SecurePassword123!"
    }
    login_res = client.post("/api/auth/login", json=login_payload)
    assert login_res.status_code == 200
    login_data = login_res.json()
    
    assert "access_token" in login_data
    assert login_data["user"]["workspace_id"] == orig_ws_id
    assert login_data["user"]["plan_id"] == "free"
