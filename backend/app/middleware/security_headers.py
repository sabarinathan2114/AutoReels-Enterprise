from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.config.settings import settings

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Enterprise HTTP Security Headers Middleware.
    Enforces Strict-Transport-Security, Content-Security-Policy, Frame-Options,
    MIME type sniffing prevention, and modern browser protections (SEC-19).
    """
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        if settings.SECURITY_HEADERS_ENABLED:
            # 1. Content Security Policy (allows self, data URIs for images, https for external models)
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "media-src 'self' blob: https:; "
                "font-src 'self' data: https:;"
            )
            # 2. Prevent MIME-sniffing
            response.headers["X-Content-Type-Options"] = "nosniff"
            # 3. Prevent clickjacking / iframe embedding
            response.headers["X-Frame-Options"] = "DENY"
            # 4. Enforce HTTPS in production browsers
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            # 5. Strict Referrer Policy
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            # 6. Restrict sensitive hardware features
            response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
            # 7. Legacy XSS block
            response.headers["X-XSS-Protection"] = "1; mode=block"

        return response
