import time
from enum import Enum
from typing import Dict, Optional

class CircuitState(str, Enum):
    CLOSED = "CLOSED"         # Normal operation, traffic allowed
    OPEN = "OPEN"             # Provider failing, fast-fail traffic and trigger fallback
    HALF_OPEN = "HALF_OPEN"   # Probing provider with limited canary traffic

class CircuitBreaker:
    """
    AutoReels v2.0 Section 4 Provider Circuit Breaker.
    Prevents cascading timeouts by fast-failing traffic to failing upstream providers.
    """
    def __init__(
        self,
        failure_threshold: int = 3,
        cooldown_seconds: float = 30.0,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.success_threshold = success_threshold

        self.failure_count = 0
        self.success_count = 0
        self.state = CircuitState.CLOSED
        self.last_state_change = time.time()

    def allow_request(self) -> bool:
        now = time.time()
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            # Check if cooldown has elapsed
            if now - self.last_state_change >= self.cooldown_seconds:
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
                self.success_count = 0
                return True
            return False
        elif self.state == CircuitState.HALF_OPEN:
            return True
        return False

    def record_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.last_state_change = time.time()
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold or self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()

class CircuitBreakerRegistry:
    _breakers: Dict[str, CircuitBreaker] = {}

    @classmethod
    def get_breaker(cls, provider_id: str) -> CircuitBreaker:
        if provider_id not in cls._breakers:
            cls._breakers[provider_id] = CircuitBreaker()
        return cls._breakers[provider_id]

    @classmethod
    def reset_all(cls):
        cls._breakers.clear()
