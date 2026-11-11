import os
import datetime
from typing import Optional, Dict, Any
import bcrypt
import jwt
from sqlalchemy.orm import Session
from app.models.entities import User

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "cosmic_reels_secret_key_8b5cf6_a855f7")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

class AuthService:
    @staticmethod
    def hash_password(plain_password: str) -> str:
        """Hashes password securely with random salt using bcrypt."""
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifies a plain password against the stored bcrypt hash."""
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8")
            )
        except Exception:
            return False

    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[datetime.timedelta] = None) -> str:
        """Generates a signed JWT token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
        else:
            expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
        """Decodes and validates a JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email.lower().strip()).first()

    @staticmethod
    def create_user(db: Session, email: str, plain_password: str, full_name: Optional[str] = None) -> User:
        hashed_pw = AuthService.hash_password(plain_password)
        db_user = User(
            email=email.lower().strip(),
            hashed_password=hashed_pw,
            full_name=full_name
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
