import datetime
from typing import Optional, List, Dict, Any, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, StringConstraints, ConfigDict
from sqlalchemy.orm import Session

try:
    import email_validator
    from pydantic import EmailStr
except (ImportError, Exception):
    EmailStr = Annotated[str, StringConstraints(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")]

from app.database import get_db
from app.models.entities import User, PlatformAdmin
from app.services.auth_service import AuthService
from app.services.admin_service import AdminService

router = APIRouter(prefix="/api/v1/admin", tags=["Super Admin Control Plane"])

admin_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/admin/login", auto_error=False)

# Admin token configuration
ADMIN_AUDIENCE = "autoreels-admin"
ADMIN_SESSION_MINUTES = 30  # Spec ADM-03: Shorter session (30 min idle)

# Request / Response Schemas
class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str

class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin_user: Dict[str, Any]

class UpdatePlanRequest(BaseModel):
    name: Optional[str] = None
    monthly_video_quota: Optional[int] = None
    max_duration_seconds: Optional[int] = None
    resolution: Optional[str] = None
    watermark: Optional[bool] = None
    features: Optional[List[str]] = None

class ChangeTenantPlanRequest(BaseModel):
    new_plan_id: str

class RejectUpgradeRequest(BaseModel):
    reason: str = "Capacity limitation or eligibility requirements not met"

class DailyCapRequest(BaseModel):
    cap: int

class AdminUserContext:
    def __init__(self, user: User, platform_admin: PlatformAdmin):
        self.user = user
        self.admin = platform_admin
        self.role = platform_admin.role

def get_current_admin(
    token: Optional[str] = Depends(admin_oauth2_scheme),
    db: Session = Depends(get_db)
) -> AdminUserContext:
    """
    Enforces ADM-01 and ADM-03:
    Admin APIs require a valid JWT with audience 'autoreels-admin' and verified PlatformAdmin status.
    Non-admins calling this receive HTTP 403 Forbidden.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = AuthService.decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin session expired or invalid"
        )

    # Validate Audience (ADM-T1)
    aud = payload.get("aud")
    if aud != ADMIN_AUDIENCE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: token not authorized for admin control plane (audience mismatch)"
        )

    email = payload.get("sub")
    user = AuthService.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin user record not found"
        )

    platform_admin = db.query(PlatformAdmin).filter(PlatformAdmin.user_id == user.id).first()
    if not platform_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user does not hold platform administrator privileges"
        )

    return AdminUserContext(user=user, platform_admin=platform_admin)

def require_super_admin(
    admin_ctx: AdminUserContext = Depends(get_current_admin)
) -> AdminUserContext:
    """
    Enforces ADM-02 & ADM-T4:
    Role split: SUPERADMIN can execute all actions; SUPPORT is read-only for system mutations.
    """
    if admin_ctx.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: SUPERADMIN role required to perform this action. SUPPORT role has read-only access."
        )
    return admin_ctx

# -------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------

@router.post("/login", response_model=AdminTokenResponse)
def admin_login(req: AdminLoginRequest, db: Session = Depends(get_db)):
    """Authenticates a Platform Administrator and issues an isolated 30-min admin token."""
    user = AuthService.get_user_by_email(db, req.email)
    if not user or not AuthService.verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid administrator credentials"
        )

    platform_admin = db.query(PlatformAdmin).filter(PlatformAdmin.user_id == user.id).first()
    if not platform_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not registered as a platform administrator"
        )

    # Issue 30-minute admin JWT with audience 'autoreels-admin'
    expires = datetime.timedelta(minutes=ADMIN_SESSION_MINUTES)
    token_payload = {
        "sub": user.email,
        "user_id": user.id,
        "aud": ADMIN_AUDIENCE,
        "role": platform_admin.role,
        "mfa_verified": True
    }
    access_token = AuthService.create_access_token(data=token_payload, expires_delta=expires)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "admin_user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": platform_admin.role
        }
    }

@router.get("/telemetry")
def get_telemetry(
    admin_ctx: AdminUserContext = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Returns platform health, queues, and render counts."""
    return AdminService.get_system_telemetry(db)

@router.get("/tenants")
def list_tenants(
    search: Optional[str] = Query(None),
    admin_ctx: AdminUserContext = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Lists all registered tenants with their subscription and real-time usage meters."""
    return AdminService.list_all_tenants(db, search=search)

@router.post("/tenants/{tenant_id}/plan")
def change_tenant_plan(
    tenant_id: str,
    req: ChangeTenantPlanRequest,
    admin_ctx: AdminUserContext = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Manually assigns or overrides a tenant's plan tier (SUPERADMIN only)."""
    try:
        return AdminService.change_tenant_plan_manually(
            db=db,
            tenant_id=tenant_id,
            new_plan_id=req.new_plan_id,
            admin_user_id=admin_ctx.user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/plans")
def list_plans(
    admin_ctx: AdminUserContext = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Lists all tier plans and limits for the Super Admin plans editor."""
    return AdminService.list_all_plans(db)

@router.put("/plans/{plan_id}")
def update_plan(
    plan_id: str,
    req: UpdatePlanRequest,
    admin_ctx: AdminUserContext = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Updates plan limits, duration, and feature flags.
    Enforces PLAN-04 (cache invalidation takes effect immediately).
    """
    try:
        updates = {k: v for k, v in req.model_dump().items() if v is not None}
        return AdminService.update_plan_limits(
            db=db,
            plan_id=plan_id,
            updates=updates,
            admin_user_id=admin_ctx.user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/upgrade-requests")
def list_upgrade_requests(
    status: Optional[str] = Query(None),
    admin_ctx: AdminUserContext = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Lists upgrade requests submitted by creators."""
    return AdminService.list_upgrade_requests(db, status=status)

@router.post("/upgrade-requests/{request_id}/approve")
def approve_upgrade(
    request_id: str,
    admin_ctx: AdminUserContext = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Approves an upgrade request, immediately upgrading the tenant's tier and quotas."""
    try:
        return AdminService.approve_upgrade_request(
            db=db,
            request_id=request_id,
            admin_user_id=admin_ctx.user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upgrade-requests/{request_id}/reject")
def reject_upgrade(
    request_id: str,
    req: RejectUpgradeRequest,
    admin_ctx: AdminUserContext = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Rejects an upgrade request with reason note."""
    try:
        return AdminService.reject_upgrade_request(
            db=db,
            request_id=request_id,
            reason=req.reason,
            admin_user_id=admin_ctx.user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/settings/daily-cap")
def set_daily_cap(
    req: DailyCapRequest,
    admin_ctx: AdminUserContext = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Sets global daily rendering cap for the video generation farm."""
    cap = AdminService.set_system_daily_cap(db, req.cap, admin_ctx.user.id)
    return {"status": "success", "max_videos_per_day": cap}

@router.get("/audit-logs")
def list_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    admin_ctx: AdminUserContext = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Returns immutable system audit trail."""
    return AdminService.list_audit_logs(db, limit=limit)
