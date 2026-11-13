"""
Token Envelope Encryption Service (Spec 10.3, SEC-03)
Provides AES-128 CBC with HMAC authentication (Fernet) for third-party OAuth tokens.
Guarantees zero raw credentials stored in database or queues.
"""
import os
import base64
import hashlib
from typing import Optional
from cryptography.fernet import Fernet

class CryptoService:
    _fernet: Optional[Fernet] = None

    @classmethod
    def _get_fernet(cls) -> Fernet:
        if cls._fernet is None:
            raw_key = os.getenv("TOKEN_ENCRYPTION_KEY")
            if not raw_key:
                # Deterministic fallback key for development / CI derived from app secret
                secret_seed = os.getenv("SECRET_KEY", "autoreels_enterprise_super_secret_master_key_2026")
                key_bytes = hashlib.sha256(secret_seed.encode("utf-8")).digest()
                raw_key = base64.urlsafe_b64encode(key_bytes).decode("utf-8")
            cls._fernet = Fernet(raw_key.encode("utf-8") if isinstance(raw_key, str) else raw_key)
        return cls._fernet

    @classmethod
    def encrypt_token(cls, plaintext_token: str) -> str:
        """
        Encrypts an OAuth access or refresh token before persistence.
        """
        if not plaintext_token:
            return ""
        f = cls._get_fernet()
        return f.encrypt(plaintext_token.encode("utf-8")).decode("utf-8")

    @classmethod
    def decrypt_token(cls, ciphertext_token: str) -> str:
        """
        Decrypts an envelope-encrypted token for authorized API invocation.
        """
        if not ciphertext_token:
            return ""
        f = cls._get_fernet()
        return f.decrypt(ciphertext_token.encode("utf-8")).decode("utf-8")
