import pytest
from app.middleware.rate_limit import limiter
from app.services.token_revocation_service import TokenRevocationService

@pytest.fixture(autouse=True)
def reset_test_state():
    """
    Ensures test isolation across test modules so that rate limiting
    and token revocations in one test do not bleed into subsequent tests.
    """
    limiter.reset()
    TokenRevocationService.reset_cache()
    yield
    limiter.reset()
    TokenRevocationService.reset_cache()
