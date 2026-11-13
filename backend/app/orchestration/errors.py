from enum import Enum
from typing import Optional

class ErrorClass(str, Enum):
    """
    AutoReels v2.0 Section 4.4 Error Classification Matrix.
    """
    TRANSIENT = "TRANSIENT"               # 429, 502, 503, timeout, network reset -> Backoff + jitter, same provider, max 3
    PROVIDER_DOWN = "PROVIDER_DOWN"       # Repeated 5xx, circuit open -> Switch provider via router fallback chain
    CONTENT_REJECTED = "CONTENT_REJECTED" # Safety filter refusal -> Rewrite prompt once, else degrade
    INVALID_INPUT = "INVALID_INPUT"       # Schema validation fails -> Regenerate step input, max 2 attempts
    QUOTA_EXHAUSTED = "QUOTA_EXHAUSTED"   # Platform daily quota -> Defer to next window with honest ETA
    AUTH_EXPIRED = "AUTH_EXPIRED"         # 401, token revoked -> Mark channel REAUTH_REQUIRED, pause schedules
    FATAL = "FATAL"                       # Platform bug, corrupt media -> Fail step, refund video quota

class StepExecutionError(Exception):
    def __init__(
        self,
        message: str,
        error_class: ErrorClass = ErrorClass.FATAL,
        retry_after_sec: Optional[float] = None,
        can_degrade: bool = True
    ):
        super().__init__(message)
        self.message = message
        self.error_class = error_class
        self.retry_after_sec = retry_after_sec
        self.can_degrade = can_degrade

def classify_exception(exc: Exception) -> ErrorClass:
    """Classifies an arbitrary exception into a standard AutoReels error class."""
    if isinstance(exc, StepExecutionError):
        return exc.error_class

    exc_str = str(exc).lower()
    if any(code in exc_str for code in ["429", "too many requests", "rate limit", "timeout", "timed out", "connection reset", "502", "503", "504"]):
        return ErrorClass.TRANSIENT
    if any(code in exc_str for code in ["circuit open", "connection refused", "provider unavailable"]):
        return ErrorClass.PROVIDER_DOWN
    if any(code in exc_str for code in ["safety", "nsfw", "moderation", "content violation"]):
        return ErrorClass.CONTENT_REJECTED
    if any(code in exc_str for code in ["invalid schema", "pydantic", "validation error"]):
        return ErrorClass.INVALID_INPUT
    if any(code in exc_str for code in ["token revoked", "invalid_grant", "401 unauthorized"]):
        return ErrorClass.AUTH_EXPIRED
    
    return ErrorClass.FATAL
