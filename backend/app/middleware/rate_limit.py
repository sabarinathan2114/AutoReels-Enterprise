import time
import threading
from typing import Dict, List, Tuple
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.settings import settings

class RateLimiter:
    """
    Sliding window rate limiter with microsecond timestamp tracking.
    Thread-safe and supports distinct rate tiers for sensitive auth vs general endpoints.
    Spec Section 10.1 & SEC-11/SEC-12.
    """
    def __init__(self):
        self._lock = threading.Lock()
        # Storage: {client_key: [(timestamp, window_seconds)]}
        self._history: Dict[str, List[float]] = {}

    def is_allowed(self, client_key: str, limit: int, window_sec: int = 60) -> Tuple[bool, int, int]:
        """
        Determines whether the client request is permitted under the sliding window.
        Returns: (allowed: bool, remaining: int, retry_after: int)
        """
        now = time.time()
        window_start = now - window_sec

        with self._lock:
            timestamps = self._history.get(client_key, [])
            # Evict timestamps older than the window
            valid_timestamps = [ts for ts in timestamps if ts > window_start]

            if len(valid_timestamps) >= limit:
                # Rate limit breached
                oldest_in_window = valid_timestamps[0]
                retry_after = max(1, int(oldest_in_window + window_sec - now))
                self._history[client_key] = valid_timestamps
                return False, 0, retry_after

            # Allow request and record timestamp
            valid_timestamps.append(now)
            self._history[client_key] = valid_timestamps
            remaining = limit - len(valid_timestamps)
            return True, remaining, window_sec

    def reset(self):
        """Resets all tracking counters (used in tests)."""
        with self._lock:
            self._history.clear()

# Global rate limiter instance
limiter = RateLimiter()

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        path = request.url.path

        # Exempt health probes, static assets, and OpenAPI docs
        if (
            path in ["/", "/health/live", "/health/ready", "/docs", "/redoc", "/openapi.json"]
            or path.startswith("/storage/")
            or path.startswith("/_next/")
        ):
            return await call_next(request)

        # Determine client identifier
        auth_header = request.headers.get("Authorization", "")
        forwarded_for = request.headers.get("X-Forwarded-For")
        client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else (request.client.host if request.client else "127.0.0.1")
        
        # Check if auth endpoint
        is_auth_endpoint = any(
            path.startswith(p) for p in [
                "/api/v1/auth/login",
                "/api/v1/auth/register",
                "/api/v1/admin/login",
                "/api/auth/login",
                "/api/auth/register",
                "/api/admin/login"
            ]
        )

        if is_auth_endpoint:
            limit = settings.RATE_LIMIT_AUTH_PER_MIN
            client_key = f"auth:{client_ip}"
        else:
            limit = settings.RATE_LIMIT_DEFAULT_PER_MIN
            client_key = f"api:{auth_header[:32] if auth_header.startswith('Bearer ') else client_ip}"

        allowed, remaining, retry_after = limiter.is_allowed(client_key, limit=limit, window_sec=60)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": f"Rate limit exceeded. Maximum {limit} requests per minute.",
                    "limit": limit,
                    "retry_after": retry_after
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(retry_after)
                }
            )

        response: Response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(retry_after)
        return response
