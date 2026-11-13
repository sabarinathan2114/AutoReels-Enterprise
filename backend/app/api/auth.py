from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, Annotated
from pydantic import BaseModel, StringConstraints, ConfigDict

try:
    import email_validator
    from pydantic import EmailStr
except (ImportError, Exception):
    EmailStr = Annotated[str, StringConstraints(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")]

from app.database import get_db
from app.models.entities import User, Channel, SocialAccount, Membership, Workspace, Subscription
from app.services.auth_service import AuthService
from app.services.tenant_service import TenantService
from app.services.token_revocation_service import TokenRevocationService

router = APIRouter(tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Schemas
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = "Creator"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    uuid: Optional[str] = None
    email: str
    full_name: Optional[str]
    is_active: bool
    workspace_id: Optional[str] = None
    plan_id: Optional[str] = "free"

    model_config = ConfigDict(from_attributes=True)

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class RevokeRequest(BaseModel):
    token: Optional[str] = None
    reason: Optional[str] = "user_logout"

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    # 1. Check if token has been revoked (SEC-22)
    if TokenRevocationService.is_token_revoked(db, token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "TOKEN_REVOKED", "message": "This token has been revoked. Please sign in again."},
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = AuthService.decode_access_token(token)
    if not payload:
        raise credentials_exception
    email: str = payload.get("sub")
    if not email:
        raise credentials_exception
    user = AuthService.get_user_by_email(db, email=email)
    if not user:
        raise credentials_exception
    return user

@router.post("/register", response_model=AuthResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = AuthService.get_user_by_email(db, req.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )
    if len(req.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )
    
    user = AuthService.create_user(db, req.email, req.password, req.full_name)
    
    # Provision tenant hierarchy with Free plan in one atomic transaction
    tenant_info = TenantService.create_tenant_hierarchy(
        db=db,
        user_id=user.id,
        tenant_name=req.full_name or "My Studio",
        plan_id="free"
    )
    workspace_id = tenant_info["workspace_id"]

    # Seed default starter channels for this new user scoped to workspace
    default_ch = Channel(
        id=f"ch_{user.id}_kids",
        workspace_id=workspace_id,
        user_id=user.id,
        name="Chutti Kuzhandhai (Tamil / Kids)",
        niche="emotional_drama",
        language="Tamil",
        default_voice="ta-IN-ValluvarNeural",
        avatar="👶"
    )
    db.add(default_ch)
    db.commit()

    token = AuthService.create_access_token(data={"sub": user.email, "user_id": user.id, "workspace_id": workspace_id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "uuid": user.uuid,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "workspace_id": workspace_id,
            "plan_id": "free"
        }
    }

@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = AuthService.get_user_by_email(db, req.email)
    if not user or not AuthService.verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Retrieve user's primary workspace and plan
    membership = db.query(Membership).filter(Membership.user_id == user.id).first()
    workspace_id = membership.workspace_id if membership else None
    
    plan_id = "free"
    if membership and membership.workspace:
        sub = db.query(Subscription).filter(Subscription.tenant_id == membership.workspace.tenant_id).first()
        if sub:
            plan_id = sub.plan_id

    token = AuthService.create_access_token(data={"sub": user.email, "user_id": user.id, "workspace_id": workspace_id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "uuid": user.uuid,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "workspace_id": workspace_id,
            "plan_id": plan_id
        }
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/revoke")
def revoke_token_endpoint(
    req: Optional[RevokeRequest] = None,
    current_token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Emergency Token Revocation Endpoint (SEC-22).
    Invalidates current session token or target compromised token.
    """
    target_token = req.token if (req and req.token) else current_token
    reason = req.reason if (req and req.reason) else "user_logout"
    TokenRevocationService.revoke_token(db, target_token, reason=reason)
    return {"status": "success", "message": "Token revoked successfully"}

