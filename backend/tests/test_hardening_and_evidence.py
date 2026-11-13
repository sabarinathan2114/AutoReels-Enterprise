import io
import time
import uuid
import concurrent.futures
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.middleware.rate_limit import limiter
from app.services.token_revocation_service import TokenRevocationService
from app.services.upload_security_service import UploadSecurityService
from app.services.tenant_service import TenantService
from app.services.auth_service import AuthService
from app.models.entities import User

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_rate_limiter_and_revocations():
    """Ensure clean state before each hardening test."""
    limiter.reset()
    TokenRevocationService.reset_cache()
    yield
    limiter.reset()
    TokenRevocationService.reset_cache()

# ========================================================
# 1. SECURITY HEADERS TEST (SEC-19)
# ========================================================
def test_security_headers_middleware():
    """
    Spec Section 10 & SEC-19:
    All HTTP responses must enforce Strict-Transport-Security, CSP,
    MIME sniffing protection, and Clickjacking denial.
    """
    response = client.get("/api/plans")
    assert response.status_code == 200
    headers = response.headers

    assert "default-src 'self'" in headers["Content-Security-Policy"]
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"
    assert "max-age=31536000" in headers["Strict-Transport-Security"]
    assert headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "camera=()" in headers["Permissions-Policy"]
    assert headers["X-XSS-Protection"] == "1; mode=block"

# ========================================================
# 2. RATE LIMITING TESTS (SEC-11, SEC-12)
# ========================================================
def test_auth_rate_limiting_sensitive_endpoints():
    """
    Spec Section 10.1 & SEC-11:
    Sensitive auth endpoints (/api/v1/auth/login, etc.) must be throttled
    to 5 requests/minute per IP, returning HTTP 429 with Retry-After header.
    """
    limiter.reset()
    custom_ip = "192.168.100.42"
    headers = {"X-Forwarded-For": custom_ip}

    # First 5 attempts are allowed through to handler (returning 401 for bad creds)
    for i in range(5):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "wrongpassword"},
            headers=headers
        )
        assert resp.status_code in [400, 401], f"Attempt {i+1} should pass rate limit"
        assert resp.headers.get("X-RateLimit-Limit") == "5"

    # 6th attempt must be blocked by rate limit middleware
    blocked_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrongpassword"},
        headers=headers
    )
    assert blocked_resp.status_code == 429
    data = blocked_resp.json()
    assert data["error"] == "RATE_LIMIT_EXCEEDED"
    assert "Retry-After" in blocked_resp.headers
    assert blocked_resp.headers.get("X-RateLimit-Remaining") == "0"

def test_api_rate_limiting_general_endpoints():
    """
    Spec Section 10.1 & SEC-12:
    General API endpoints are capped at 60 requests/minute per client.
    """
    limiter.reset()
    custom_ip = "192.168.200.88"
    headers = {"X-Forwarded-For": custom_ip}

    # Fire 60 requests
    for _ in range(60):
        resp = client.get("/api/plans", headers=headers)
        assert resp.status_code == 200

    # 61st request hits 429
    blocked = client.get("/api/plans", headers=headers)
    assert blocked.status_code == 429
    assert blocked.json()["error"] == "RATE_LIMIT_EXCEEDED"

# ========================================================
# 3. UPLOAD SECURITY & MAGIC BYTES (SEC-14)
# ========================================================
def test_upload_security_filename_sanitization():
    """
    Spec Section 10 & SEC-14:
    Filenames with path traversal, directory separators, or null bytes
    must be strictly neutralized.
    """
    # Null byte rejection
    with pytest.raises(Exception) as excinfo:
        UploadSecurityService.sanitize_filename("test\0bad.png")
    assert "illegal null bytes" in str(excinfo.value.detail)

    # Path traversal stripping
    sanitized = UploadSecurityService.sanitize_filename("../../etc/passwd.png")
    assert ".." not in sanitized
    assert "/" not in sanitized
    assert "\\" not in sanitized
    assert sanitized == "passwd.png"

def test_upload_security_magic_bytes_validation():
    """
    Spec Section 10 & SEC-14:
    File magic bytes must match declared file type; fake extensions must fail.
    """
    # Fake PNG: plain text pretending to be a PNG
    fake_png = b"This is plain text and not a genuine PNG image."
    with pytest.raises(Exception) as excinfo:
        UploadSecurityService.validate_upload(fake_png, "avatar.png", category="image")
    assert "INVALID_FILE_SIGNATURE" in str(excinfo.value.detail)

    # Valid PNG: magic bytes header \x89PNG\r\n\x1a\n
    valid_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\x00" * 32
    res = UploadSecurityService.validate_upload(valid_png, "avatar.png", category="image")
    assert res["valid"] is True
    assert res["extension"] == "png"

# ========================================================
# 4. TOKEN REVOCATION LIFECYCLE (SEC-22)
# ========================================================
def test_emergency_token_revocation_lifecycle():
    """
    Spec Section 10 & SEC-22:
    Compromised tokens can be revoked immediately, permanently denying further requests.
    """
    db = SessionLocal()
    try:
        # Register a test user
        email = f"compromised_{uuid.uuid4().hex[:6]}@example.com"
        reg_resp = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "SecurePassword123!", "full_name": "Test Revoke"}
        )
        assert reg_resp.status_code == 200
        token = reg_resp.json()["access_token"]
        auth_header = {"Authorization": f"Bearer {token}"}

        # 1. Access before revocation -> 200 OK
        me_resp = client.get("/api/auth/me", headers=auth_header)
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == email

        # 2. Call emergency revocation endpoint
        revoke_resp = client.post("/api/auth/revoke", headers=auth_header)
        assert revoke_resp.status_code == 200
        assert revoke_resp.json()["status"] == "success"

        # 3. Access after revocation -> 401 TOKEN_REVOKED
        post_revoke_resp = client.get("/api/auth/me", headers=auth_header)
        assert post_revoke_resp.status_code == 401
        err_detail = post_revoke_resp.json()["detail"]
        assert err_detail.get("error") == "TOKEN_REVOKED"
    finally:
        db.close()

# ========================================================
# 5. HIGH-CONCURRENCY STRESS / BURST TEST
# ========================================================
def test_burst_concurrency_stress_load():
    """
    Phase 10 Hardening & Evidence:
    Simulates a high burst of 50 concurrent requests hitting the platform.
    Verifies 100% availability, zero unhandled 500 exceptions, and thread safety.
    """
    def make_request(worker_id: int):
        # Use distinct IP per worker to test concurrency without artificial IP rate limiting
        headers = {"X-Forwarded-For": f"10.50.{worker_id // 256}.{worker_id % 256}"}
        return client.get("/api/plans", headers=headers)

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(make_request, i) for i in range(50)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    # All 50 requests must succeed with 200 OK
    assert len(results) == 50
    for r in results:
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 4  # 4 plans returned reliably
