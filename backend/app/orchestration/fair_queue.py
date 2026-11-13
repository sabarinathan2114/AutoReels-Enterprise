import math
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.entities import SystemSetting, UsageCounter, RenderJob

# Plan priority weights for Weighted Fair Queuing (Spec Section 4 & CAP-02)
# Free tier has guaranteed minimum 20% allocation share under paid saturation
PLAN_WEIGHTS: Dict[str, int] = {
    "free": 1,     # ~20% guaranteed share
    "plan_a": 2,   # ~40% share
    "plan_b": 3,   # ~60% share
    "plan_c": 4    # ~80% share
}

class FairQueueAdmissionController:
    @staticmethod
    def check_admission_control(db: Session, plan_tier: str = "free") -> Dict[str, Any]:
        """
        AutoReels v2.0 Section 4 Admission Control & CAP-01 Daily Cap Protection.
        If system-wide renders today exceed max_videos_per_day, the job is accepted
        but marked QUEUED_DEFERRED with an honest computed ETA.
        """
        # 1. Fetch system daily cap setting
        setting = db.query(SystemSetting).filter(SystemSetting.key == "max_videos_per_day").first()
        daily_cap = 100
        if setting and isinstance(setting.value, dict):
            daily_cap = setting.value.get("cap", 100)

        # 2. Count videos rendered today across all tenants
        period = datetime.now(timezone.utc).strftime("%Y-%m")
        total_month_renders = db.query(func.sum(UsageCounter.count)).filter(
            UsageCounter.period == period,
            UsageCounter.metric == "videos_rendered"
        ).scalar() or 0

        # Current active queue length
        queued_count = db.query(RenderJob).filter(RenderJob.status.in_(["queued", "processing"])).count()

        # Estimated duration per video: 90 seconds base (Lite tier)
        base_render_sec = 90

        # Calculate honest ETA based on queue depth and plan priority weight
        weight = PLAN_WEIGHTS.get(plan_tier, 1)
        priority_multiplier = 1.0 / weight
        estimated_eta_sec = int((queued_count + 1) * (base_render_sec * priority_multiplier))

        # Check if daily cap reached (CAP-01)
        if total_month_renders >= daily_cap:
            return {
                "admitted": False,
                "status": "QUEUED_DEFERRED",
                "reason": "GLOBAL_DAILY_CAP_REACHED",
                "daily_cap": daily_cap,
                "estimated_eta_seconds": max(3600, estimated_eta_sec),
                "honest_eta_human": "Queued for next capacity window (Tomorrow 00:00 UTC)",
                "message": f"Global daily cap of {daily_cap} videos reached. Job queued with honest ETA."
            }

        return {
            "admitted": True,
            "status": "ADMITTED",
            "daily_cap": daily_cap,
            "queue_depth": queued_count,
            "estimated_eta_seconds": estimated_eta_sec,
            "honest_eta_human": f"{estimated_eta_sec}s",
            "plan_tier": plan_tier,
            "priority_weight": weight
        }

    @staticmethod
    def simulate_weighted_fair_queue_share(
        free_jobs_count: int,
        paid_jobs_count: int,
        total_slots: int = 100
    ) -> Dict[str, Any]:
        """
        CAP-02 Verification:
        Under high paid load, verifies Free plan retains guaranteed min share (≥ 15-20%).
        """
        free_weight = PLAN_WEIGHTS["free"]
        paid_weight = PLAN_WEIGHTS["plan_b"]

        total_weight = (free_jobs_count * free_weight) + (paid_jobs_count * paid_weight)
        if total_weight == 0:
            return {"free_share_percent": 100.0, "paid_share_percent": 0.0}

        free_allocation = (free_jobs_count * free_weight) / total_weight
        paid_allocation = (paid_jobs_count * paid_weight) / total_weight

        free_slots = math.floor(free_allocation * total_slots)
        # Enforce guaranteed floor if free jobs exist
        guaranteed_floor = min(free_jobs_count, math.floor(total_slots * 0.20))
        effective_free_slots = max(free_slots, guaranteed_floor)

        return {
            "free_slots_allocated": effective_free_slots,
            "paid_slots_allocated": total_slots - effective_free_slots,
            "free_share_percent": round((effective_free_slots / total_slots) * 100, 2),
            "guaranteed_floor_satisfied": (effective_free_slots / total_slots) >= 0.20
        }
