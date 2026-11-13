"""
Social Channels API Router (Spec Section 8, Section 15.4)
Handles Google OAuth PKCE initiation, channel connectivity, health monitoring,
and quota-governed YouTube Resumable Upload publishing.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entities import SocialAccount
from app.services.channel_service import ChannelService
from app.services.social_publisher import PublishResult

router = APIRouter(prefix="/api/v1/social", tags=["Social Channels & Publishing"])

class OAuthInitRequest(BaseModel):
    workspace_id: str
    user_id: int

class ConnectChannelRequest(BaseModel):
    workspace_id: str
    user_id: int
    platform: str = "youtube"
    account_name: str
    handle: Optional[str] = None
    access_token: str
    refresh_token: str

class ChannelPublishRequest(BaseModel):
    video_path: str
    title: str
    description: Optional[str] = ""
    tags: Optional[List[str]] = []

@router.post("/oauth/google/init")
def initiate_google_oauth(req: OAuthInitRequest):
    """
    Spec Phase 9: Google OAuth PKCE generation.
    Returns authorization URL and state token.
    """
    return ChannelService.generate_google_oauth_url(req.workspace_id, req.user_id)

@router.post("/channels/connect", status_code=status.HTTP_201_CREATED)
def connect_social_channel(req: ConnectChannelRequest, db: Session = Depends(get_db)):
    """
    Connects a new social channel.
    Enforces plan entitlement (FEATURE_LOCKED for Free plan, channel limits for Plan A/B/C).
    Stores credentials envelope-encrypted with Fernet (SEC-03).
    """
    account = ChannelService.connect_channel(
        db=db,
        workspace_id=req.workspace_id,
        user_id=req.user_id,
        platform=req.platform,
        account_name=req.account_name,
        handle=req.handle or f"@{req.account_name.lower().replace(' ', '')}",
        raw_access_token=req.access_token,
        raw_refresh_token=req.refresh_token
    )
    return {
        "id": account.id,
        "workspace_id": account.workspace_id,
        "platform": account.platform,
        "account_name": account.account_name,
        "handle": account.handle,
        "health_status": account.health_status,
        "privacy_status": account.privacy_status,
        "is_connected": account.is_connected
    }

@router.get("/channels")
def list_workspace_channels(workspace_id: str, db: Session = Depends(get_db)):
    """
    Lists connected channels for a workspace with current health and privacy status.
    Never exposes raw or decrypted tokens in output.
    """
    channels = db.query(SocialAccount).filter(
        SocialAccount.workspace_id == workspace_id,
        SocialAccount.is_connected == True
    ).all()

    return [
        {
            "id": c.id,
            "platform": c.platform,
            "account_name": c.account_name,
            "handle": c.handle,
            "health_status": c.health_status,
            "privacy_status": c.privacy_status,
            "daily_published_count": c.daily_published_count,
            "last_published_at": c.last_published_at.isoformat() if c.last_published_at else None
        }
        for c in channels
    ]

@router.post("/channels/{channel_id}/publish", response_model=PublishResult)
async def publish_to_channel(
    channel_id: str,
    req: ChannelPublishRequest,
    db: Session = Depends(get_db)
):
    """
    Dispatches reel through YouTube Resumable Upload protocol.
    Enforces daily channel limit (6/day) and transitions health on token rejection.
    """
    return await ChannelService.publish_video_to_channel(
        db=db,
        account_id=channel_id,
        video_path=req.video_path,
        title=req.title,
        description=req.description or "",
        tags=req.tags or []
    )
