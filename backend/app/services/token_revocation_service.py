import hashlib
import jwt
from datetime import datetime, timezone
from typing import Optional, Set
from sqlalchemy.orm import Session
from app.models.entities import RevokedToken
from app.config.settings import settings

# In-memory fast cache for revoked token hashes
_REVOKED_HASHES: Set[str] = set()

class TokenRevocationService:
    """
    Emergency Token Revocation Service (SEC-22).
    Tracks revoked/compromised JWT tokens with in-memory O(1) checks and persistent MySQL audit records.
    """

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.strip().encode("utf-8")).hexdigest()

    @classmethod
    def revoke_token(
        cls,
        db: Session,
        token: str,
        user_id: Optional[int] = None,
        reason: str = "user_logout"
    ) -> RevokedToken:
        token_hash = cls._hash_token(token)
        _REVOKED_HASHES.add(token_hash)

        # Attempt to decode expiration from token
        expires_at = None
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            exp = payload.get("exp")
            if exp:
                expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
        except Exception:
            pass

        # Check if already present in DB
        existing = db.query(RevokedToken).filter(RevokedToken.token_hash == token_hash).first()
        if existing:
            return existing

        revoked = RevokedToken(
            token_hash=token_hash,
            user_id=user_id,
            expires_at=expires_at,
            reason=reason
        )
        db.add(revoked)
        db.commit()
        db.refresh(revoked)
        return revoked

    @classmethod
    def is_token_revoked(cls, db: Session, token: str) -> bool:
        if not token:
            return False
        token_hash = cls._hash_token(token)

        # 1. Fast in-memory check
        if token_hash in _REVOKED_HASHES:
            return True

        # 2. Database lookup
        revoked = db.query(RevokedToken).filter(RevokedToken.token_hash == token_hash).first()
        if revoked:
            _REVOKED_HASHES.add(token_hash)
            return True

        return False

    @classmethod
    def reset_cache(cls):
        """Clears in-memory cache (for testing)."""
        _REVOKED_HASHES.clear()
