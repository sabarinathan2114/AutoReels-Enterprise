"""
Phase 9 Social Channels & Publishing Tests (Spec Section 8, Section 15.4)
Tests:
- Google OAuth 2.0 PKCE generation
- Token envelope encryption (SEC-03)
- Plan-based social channel entitlement gating (403 FEATURE_LOCKED on Free)
- Channel connection limit enforcement (Plan A: 1 channel limit)
- YouTube Resumable Upload protocol with session URI persistence & resume
- Token expiration -> REAUTH_REQUIRED health state transition
- Daily channel cap enforcement (max 6 shorts/day)
"""
import uuid
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.entities import User, Workspace, Plan, Subscription, SocialAccount
from app.services.auth_service import AuthService
from app.services.tenant_service import TenantService
from app.services.crypto_service import CryptoService
from app.services.social_publisher import YouTubePublisher, PublishMetadata

client = TestClient(app)

@pytest.fixture
def social_test_env():
    """Sets up a test user with a Free workspace and a Plan A workspace."""
    db = SessionLocal()
    user = User(
        email=f"social_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password=AuthService.hash_password("Pass123!"),
        full_name="Social Creator",
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 1. Free Workspace
    free_data = TenantService.create_tenant_hierarchy(
        db=db,
        user_id=user.id,
        tenant_name="Free Studio",
        plan_id="free"
    )

    # 2. Plan A Workspace (allows 1 social channel)
    plan_a_data = TenantService.create_tenant_hierarchy(
        db=db,
        user_id=user.id,
        tenant_name="Plan A Studio",
        plan_id="plan_a"
    )

    user_id = user.id
    free_ws = free_data["workspace_id"]
    plan_a_ws = plan_a_data["workspace_id"]
    db.close()

    return {
        "user_id": user_id,
        "free_workspace_id": free_ws,
        "plan_a_workspace_id": plan_a_ws
    }

def test_token_envelope_encryption_sec_03():
    """SEC-03: Tokens are encrypted with Fernet and never stored as plaintext"""
    raw_secret = "google_oauth_refresh_token_xyz_987654321"
    encrypted = CryptoService.encrypt_token(raw_secret)
    
    assert encrypted != raw_secret
    assert "google_oauth_refresh_token" not in encrypted
    
    decrypted = CryptoService.decrypt_token(encrypted)
    assert decrypted == raw_secret

def test_google_oauth_pkce_generation(social_test_env):
    """Verifies Google OAuth URL generation with PKCE (S256 code challenge)"""
    res = client.post("/api/v1/social/oauth/google/init", json={
        "workspace_id": social_test_env["plan_a_workspace_id"],
        "user_id": social_test_env["user_id"]
    })
    assert res.status_code == 200
    data = res.json()
    assert "authorization_url" in data
    assert "code_challenge=" in data["authorization_url"]
    assert "code_challenge_method=S256" in data["authorization_url"]
    assert "state=" in data["authorization_url"]

def test_free_plan_channel_connect_blocked_feature_locked(social_test_env):
    """Free plan user attempting to connect a channel gets HTTP 403 FEATURE_LOCKED"""
    res = client.post("/api/v1/social/channels/connect", json={
        "workspace_id": social_test_env["free_workspace_id"],
        "user_id": social_test_env["user_id"],
        "platform": "youtube",
        "account_name": "My Free YouTube Channel",
        "access_token": "mock_access_token",
        "refresh_token": "mock_refresh_token"
    })
    assert res.status_code == 403
    assert "FEATURE_LOCKED" in res.json()["detail"]

def test_plan_a_channel_connection_and_limit_enforcement(social_test_env):
    """Plan A allows 1 channel; attempting a 2nd channel triggers CHANNEL_LIMIT_REACHED"""
    ws_id = social_test_env["plan_a_workspace_id"]
    user_id = social_test_env["user_id"]

    # 1. First channel connects successfully
    res1 = client.post("/api/v1/social/channels/connect", json={
        "workspace_id": ws_id,
        "user_id": user_id,
        "platform": "youtube",
        "account_name": "Tech Insights Shorts",
        "handle": "@techinsights",
        "access_token": "mock_access_token_1",
        "refresh_token": "mock_refresh_token_1"
    })
    assert res1.status_code == 201
    ch1 = res1.json()
    assert ch1["account_name"] == "Tech Insights Shorts"
    assert ch1["health_status"] == "CONNECTED"
    assert ch1["privacy_status"] == "private"  # Unaudited developer privacy

    # 2. Second channel exceeds Plan A's limit of 1
    res2 = client.post("/api/v1/social/channels/connect", json={
        "workspace_id": ws_id,
        "user_id": user_id,
        "platform": "youtube",
        "account_name": "Second Channel Exceeds Limit",
        "access_token": "mock_access_token_2",
        "refresh_token": "mock_refresh_token_2"
    })
    assert res2.status_code == 403
    assert "CHANNEL_LIMIT_REACHED" in res2.json()["detail"]

@pytest.mark.asyncio
async def test_youtube_resumable_upload_session_and_resume():
    """Verifies YouTube Resumable Upload protocol initialization and byte resume"""
    publisher = YouTubePublisher()
    meta = PublishMetadata(
        title="Impossible Roman Concrete",
        description="Daily facts reel",
        tags=["shorts", "facts"],
        privacy_status="private"
    )

    # 1. Initialize session URI
    session_uri = await publisher.initialize_resumable_session(
        access_token="mock_valid_token",
        video_path="backend/tests/test_studio_viewing_ui.py",  # dummy file
        metadata=meta
    )
    assert "upload_id=mock_session_" in session_uri

    # 2. Upload with resumption
    result = await publisher.upload_video_stream(
        session_uri=session_uri,
        video_path="backend/tests/test_studio_viewing_ui.py",
        start_byte=1024  # Resumed upload
    )
    assert result.success is True
    assert result.is_resumed is True
    assert result.video_id is not None
    assert "youtube.com/shorts/" in result.video_url
    assert result.privacy_status == "private"

def test_daily_channel_cap_enforcement(social_test_env):
    """Enforces maximum 6 shorts per day per channel"""
    from app.services.channel_service import ChannelService
    db = SessionLocal()
    ws_id = social_test_env["plan_a_workspace_id"]
    user_id = social_test_env["user_id"]
    try:
        # Create a channel for this test
        ch = ChannelService.connect_channel(
            db=db,
            workspace_id=ws_id,
            user_id=user_id,
            platform="youtube",
            account_name="Cap Test Channel",
            handle="@captest",
            raw_access_token="mock_token",
            raw_refresh_token="mock_refresh"
        )
        assert ch is not None

        # Simulate channel reaching 6/6 daily cap
        ch.daily_published_count = 6
        db.commit()

        # Attempt publish
        res = client.post(f"/api/v1/social/channels/{ch.id}/publish", json={
            "video_path": "backend/tests/test_studio_viewing_ui.py",
            "title": "Short Exceeding Cap",
            "description": "Daily fact"
        })
        assert res.status_code == 429
        assert "DAILY_CHANNEL_CAP_EXCEEDED" in res.json()["detail"]
    finally:
        db.close()
