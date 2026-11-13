import logging
from typing import List, Dict, Any, Optional
from app.orchestration.circuit_breaker import CircuitBreakerRegistry, CircuitState

logger = logging.getLogger("autoreels.router")

# Default Zero-Cost / Open-Source Fallback Chains (Spec Section 4 & Section 15)
DEFAULT_FALLBACK_CHAINS: Dict[str, List[Dict[str, Any]]] = {
    "script": [
        {"id": "ollama_local", "cost_micros": 0, "name": "Local Ollama Llama 3"},
        {"id": "llama_cpp", "cost_micros": 0, "name": "Embedded llama.cpp"},
        {"id": "deterministic_fallback", "cost_micros": 0, "name": "Deterministic Template Fallback"}
    ],
    "image": [
        {"id": "flux_schnell", "cost_micros": 0, "name": "Flux Schnell (Local / Free)"},
        {"id": "pollock_stock", "cost_micros": 0, "name": "Free Curated Stock Engine"},
        {"id": "solid_color_degrade", "cost_micros": 0, "name": "Solid-Color Motion Canvas (Degraded)"}
    ],
    "tts": [
        {"id": "piper_tts", "cost_micros": 0, "name": "Piper Neural TTS (Local CPU)"},
        {"id": "edge_tts", "cost_micros": 0, "name": "Edge TTS Free Cloud Fallback"},
        {"id": "kokoro_tts", "cost_micros": 0, "name": "Kokoro 82M CPU TTS"}
    ],
    "align": [
        {"id": "faster_whisper", "cost_micros": 0, "name": "Faster-Whisper Subtitle Alignment"},
        {"id": "character_heuristic", "cost_micros": 0, "name": "Pacing & Duration Heuristic Alignment"}
    ],
    "compose": [
        {"id": "ffmpeg_libass", "cost_micros": 0, "name": "FFmpeg + Libass Karaoke Render"}
    ]
}

# Maximum budget guard in micro-cents ($0.01 = 10,000 micros)
TIER_BUDGET_GUARDS: Dict[str, int] = {
    "free": 0,           # Strict zero cost (Spec Section 15.8)
    "plan_a": 50_000,    # $0.05 max per video
    "plan_b": 100_000,   # $0.10 max per video
    "plan_c": 250_000    # $0.25 max per video
}

class ProviderRouter:
    @staticmethod
    def get_candidate_providers(step_key: str, plan_tier: str = "free") -> List[Dict[str, Any]]:
        chain = DEFAULT_FALLBACK_CHAINS.get(step_key, [])
        max_budget = TIER_BUDGET_GUARDS.get(plan_tier, 0)

        candidates = []
        for p in chain:
            breaker = CircuitBreakerRegistry.get_breaker(p["id"])
            if not breaker.allow_request():
                logger.warning(f"Skipping provider {p['id']} for {step_key}: circuit is {breaker.state.value}")
                continue
            if p["cost_micros"] > max_budget:
                logger.warning(f"Skipping provider {p['id']}: cost {p['cost_micros']} exceeds budget {max_budget}")
                continue
            candidates.append(p)

        return candidates

    @staticmethod
    def record_provider_result(provider_id: str, success: bool):
        breaker = CircuitBreakerRegistry.get_breaker(provider_id)
        if success:
            breaker.record_success()
        else:
            breaker.record_failure()
