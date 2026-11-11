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
from app.models.entities import User, Channel, SocialAccount
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

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
    email: str
    full_name: Optional[str]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
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
    
    # Seed default starter channels for this new user
    default_ch = Channel(
        id=f"ch_{user.id}_kids",
        user_id=user.id,
        name="Chutti Kuzhandhai (Tamil / Kids)",
        niche="emotional_drama",
        language="Tamil",
        default_voice="ta-IN-ValluvarNeural",
        avatar="👶"
    )
    db.add(default_ch)
    db.commit()

    token = AuthService.create_access_token(data={"sub": user.email, "user_id": user.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = AuthService.get_user_by_email(db, req.email)
    if not user or not AuthService.verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    token = AuthService.create_access_token(data={"sub": user.email, "user_id": user.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
