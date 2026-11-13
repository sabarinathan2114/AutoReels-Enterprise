"""
Channel Service (Spec Section 8, Section 10.2, 10.3)
Manages social channel connections, Google OAuth PKCE generation, envelope-encrypted tokens,
channel health lifecycle, and quota/rate-limited publishing with jitter.
"""
import os
import uuid
import secrets
import hashlib
import base64
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.entities import SocialAccount, Workspace
from app.services.crypto_service import CryptoService
from app.services.entitlement_service import EntitlementService
from app.services.social_publisher import YouTubePublisher, MetaPublisher, PublishMetadata, PublishResult

class ChannelService:
    # State cache for OAuth PKCE verification
    _oauth_states: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def generate_google_oauth_url(cls, workspace_id: str, user_id: int) -> Dict[str, str]:
        """
        Generates Google OAuth 2.0 URL with PKCE (RFC 7636).
        """
        # 1. Generate code_verifier and code_challenge
        code_verifier = secrets.token_urlsafe(64)
        code_challenge_bytes = hashlib.sha256(code_verifier.encode("ascii")).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge_bytes).decode("ascii").rstrip("=")

        state = secrets.token_urlsafe(32)
        cls._oauth_states[state] = {
            "workspace_id": workspace_id,
            "user_id": user_id,
            "code_verifier": code_verifier,
            "created_at": datetime.now(timezone.utc)
        }

        client_id = os.getenv("GOOGLE_CLIENT_ID", "mock_google_client_id.apps.googleusercontent.com")
        redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/social/oauth/google/callback")
        scope = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly"

        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope={scope}&"
            f"access_type=offline&"
            f"prompt=consent&"
            f"state={state}&"
            f"code_challenge={code_challenge}&"
            f"code_challenge_method=S256"
        )

        return {
            "authorization_url": auth_url,
            "state": state
        }

    @classmethod
    def connect_channel(
        cls,
        db: Session,
        workspace_id: str,
        user_id: int,
        platform: str,
        account_name: str,
        handle: str,
        raw_access_token: str,
        raw_refresh_token: str
    ) -> SocialAccount:
        """
        Connects a channel ensuring plan entitlement (social_channels limit).
        Stores tokens with envelope encryption (SEC-03).
        """
        # 1. Enforce Entitlement Gate
        entitlements = EntitlementService.get_effective_entitlements(db, workspace_id)
        channel_limit = entitlements.get("allowed_channels_count", entitlements.get("social_channels", 0))

        if channel_limit <= 0:
            raise HTTPException(
                status_code=403,
                detail="FEATURE_LOCKED: Your current plan does not include social channels. Please upgrade to Plan A, B, or C."
            )

        current_count = db.query(SocialAccount).filter(
            SocialAccount.workspace_id == workspace_id,
            SocialAccount.is_connected == True
        ).count()

        if current_count >= channel_limit:
            raise HTTPException(
                status_code=403,
                detail=f"CHANNEL_LIMIT_REACHED: Your plan allows a maximum of {channel_limit} connected channel(s)."
            )

        # 2. Envelope-Encrypt Tokens (SEC-03)
        enc_access = CryptoService.encrypt_token(raw_access_token)
        enc_refresh = CryptoService.encrypt_token(raw_refresh_token)

        account = SocialAccount(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            user_id=user_id,
            platform=platform,
            account_name=account_name,
            handle=handle,
            access_token=enc_access,
            refresh_token=enc_refresh,
            is_connected=True,
            health_status="CONNECTED",
            privacy_status="private",  # Unaudited developer projects default to private
            daily_published_count=0
        )
        db.add(account)
        db.commit()
        db.refresh(account)
        return account

    @classmethod
    async def publish_video_to_channel(
        cls,
        db: Session,
        account_id: str,
        video_path: str,
        title: str,
        description: str,
        tags: List[str]
    ) -> PublishResult:
        """
        Dispatches video through YouTube Resumable Upload protocol.
        Enforces 6 shorts/day cap and updates channel health on failure.
        """
        account = db.query(SocialAccount).filter(SocialAccount.id == account_id).first()
        if not account or not account.is_connected:
            raise HTTPException(status_code=404, detail="Connected social account not found")

        # Check daily cap
        if account.daily_published_count >= 6:
            raise HTTPException(
                status_code=429,
                detail="DAILY_CHANNEL_CAP_EXCEEDED: Maximum 6 shorts per day reached for this channel."
            )

        # Decrypt access token
        access_token = CryptoService.decrypt_token(account.access_token) if account.access_token else ""

        publisher = YouTubePublisher() if account.platform == "youtube" else MetaPublisher()

        # Check channel health first
        health = await publisher.check_channel_health(access_token)
        account.health_status = health
        if health == "REAUTH_REQUIRED":
            db.commit()
            raise HTTPException(
                status_code=401,
                detail="REAUTH_REQUIRED: Channel credentials have expired or been revoked. Please reconnect."
            )

        # Step 1: Resumable session URI
        metadata = PublishMetadata(
            title=title,
            description=description,
            tags=tags,
            privacy_status=account.privacy_status
        )
        session_uri = await publisher.initialize_resumable_session(access_token, video_path, metadata)
        account.resumable_session_uri = session_uri
        db.commit()

        # Step 2: Upload bytes
        res = await publisher.upload_video_stream(session_uri, video_path)
        if res.success:
            account.daily_published_count += 1
            account.last_published_at = datetime.now(timezone.utc)
            account.resumable_session_uri = None
            db.commit()

        return res
