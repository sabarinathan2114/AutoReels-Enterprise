from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from pydantic import BaseModel

from app.database import get_db
from app.models.entities import Workspace, Tenant, PlanChangeRequest, Plan, Membership
from app.services.entitlement_service import EntitlementService
from app.api.auth import get_current_user, User

from fastapi.security import OAuth2PasswordBearer
from app.services.auth_service import AuthService

oauth2_optional_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def get_current_user_optional(token: Optional[str] = Depends(oauth2_optional_scheme), db: Session = Depends(get_db)) -> Optional[User]:
    if not token:
        return None
    try:
        payload = AuthService.decode_access_token(token)
        if not payload:
            return None
        return AuthService.get_user_by_email(db, email=payload.get("sub"))
    except Exception:
        return None

router = APIRouter(prefix="/api/v1", tags=["Entitlements & Quotas"])

class UpgradeRequestBody(BaseModel):
    requested_plan_id: str
    notes: Optional[str] = "Request submitted from dashboard"

@router.get("/me/entitlements")
def get_my_entitlements(
    workspace_id: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Returns effective entitlements, current period usage, and remaining quota.
    """
    target_ws = workspace_id
    if not target_ws:
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication or workspace_id required")
        # Retrieve primary workspace for current user
        membership = db.query(Membership).filter(Membership.user_id == current_user.id).first()
        if not membership:
            raise HTTPException(status_code=404, detail="No workspace found for user")
        target_ws = membership.workspace_id

    entitlements = EntitlementService.get_effective_entitlements(db, target_ws)
    return entitlements

@router.post("/workspaces/{workspace_id}/consume-quota")
def consume_workspace_quota(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """
    Atomically consumes 1 video quota. Raises 429 MONTHLY_QUOTA_EXCEEDED if limit reached.
    """
    return EntitlementService.consume_video_quota(db, workspace_id)

@router.post("/workspaces/{workspace_id}/upgrade-request", status_code=status.HTTP_201_CREATED)
def submit_upgrade_request(
    workspace_id: str,
    body: UpgradeRequestBody,
    db: Session = Depends(get_db)
):
    """
    Submits an upgrade request for platform administrator review (Plans as Data).
    """
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    target_plan = db.query(Plan).filter(Plan.id == body.requested_plan_id).first()
    if not target_plan:
        raise HTTPException(status_code=400, detail=f"Invalid plan ID: {body.requested_plan_id}")

    # Look up primary owner of workspace
    owner_membership = db.query(Membership).filter(
        Membership.workspace_id == workspace_id,
        Membership.role == "OWNER"
    ).first()
    user_id = owner_membership.user_id if owner_membership else 1

    req = PlanChangeRequest(
        tenant_id=workspace.tenant_id,
        user_id=user_id,
        requested_plan_id=body.requested_plan_id,
        status="pending",
        notes=body.notes
    )
    db.add(req)
    db.commit()
    db.refresh(req)

    return {
        "status": "pending",
        "request_id": req.id,
        "tenant_id": req.tenant_id,
        "requested_plan_id": req.requested_plan_id,
        "plan_name": target_plan.name,
        "created_at": req.created_at.isoformat() if req.created_at else None
    }
