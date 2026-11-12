import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.entities import Plan

logger = logging.getLogger("autoreels.plans")

DEFAULT_PLANS: List[Dict[str, Any]] = [
    {
        "id": "free",
        "name": "Free Tier",
        "monthly_price_cents": 0,
        "monthly_video_quota": 2,
        "max_duration_seconds": 30,
        "resolution": "720x1280",
        "watermark": True,
        "allowed_voices_count": 2,
        "allowed_channels_count": 0,
        "storage_retention_days": 3,
        "is_active": True,
        "features": ["zero_input", "preset_niches", "direct_download"]
    },
    {
        "id": "plan_a",
        "name": "Plan A (Creator)",
        "monthly_price_cents": 900,
        "monthly_video_quota": 30,
        "max_duration_seconds": 45,
        "resolution": "1080x1920",
        "watermark": False,
        "allowed_voices_count": 6,
        "allowed_channels_count": 1,
        "storage_retention_days": 14,
        "is_active": True,
        "features": ["zero_input", "director_mode", "custom_script", "single_channel_auto_dispatch"]
    },
    {
        "id": "plan_b",
        "name": "Plan B (Growth)",
        "monthly_price_cents": 2900,
        "monthly_video_quota": 100,
        "max_duration_seconds": 60,
        "resolution": "1080x1920",
        "watermark": False,
        "allowed_voices_count": 12,
        "allowed_channels_count": 3,
        "storage_retention_days": 30,
        "is_active": True,
        "features": ["zero_input", "director_mode", "character_mode", "multi_channel_auto_dispatch", "smart_scheduler"]
    },
    {
        "id": "plan_c",
        "name": "Plan C (Agency / Enterprise)",
        "monthly_price_cents": 7900,
        "monthly_video_quota": 500,
        "max_duration_seconds": 60,
        "resolution": "1080x1920",
        "watermark": False,
        "allowed_voices_count": 100,
        "allowed_channels_count": 10,
        "storage_retention_days": 60,
        "is_active": True,
        "features": ["zero_input", "director_mode", "character_mode", "custom_brand_voice", "multi_account_dispatch", "performance_autopilot", "priority_queue"]
    }
]

class PlanService:
    @staticmethod
    def seed_plans(db: Session) -> List[Plan]:
        """Seeds or updates the default 4 plan tiers per Master Spec 15.4."""
        seeded = []
        for pdata in DEFAULT_PLANS:
            plan = db.query(Plan).filter(Plan.id == pdata["id"]).first()
            if not plan:
                plan = Plan(**pdata)
                db.add(plan)
                logger.info(f"Seeded plan tier: {plan.id} ({plan.name})")
            else:
                # Update limits if altered
                for k, v in pdata.items():
                    setattr(plan, k, v)
            seeded.append(plan)
        db.commit()
        return seeded

    @staticmethod
    def get_all_active_plans(db: Session) -> List[Plan]:
        """Returns all active plans ordered by price."""
        return db.query(Plan).filter(Plan.is_active == True).order_by(Plan.monthly_price_cents.asc()).all()

    @staticmethod
    def get_plan_by_id(db: Session, plan_id: str) -> Optional[Plan]:
        return db.query(Plan).filter(Plan.id == plan_id).first()
