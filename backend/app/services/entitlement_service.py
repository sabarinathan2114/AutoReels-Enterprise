import uuid
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException, status, Depends

from app.database import get_db
from app.models.entities import Workspace, Tenant, Subscription, Plan, UsageCounter, PlanChangeRequest
from app.services.plan_service import PlanService

# In-memory entitlement cache: {workspace_id: (timestamp, data)}
_ENTITLEMENT_CACHE: Dict[str, tuple[float, Dict[str, Any]]] = {}
CACHE_TTL_SECONDS = 60

class EntitlementService:
    @staticmethod
    def get_effective_entitlements(db: Session, workspace_id: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Calculates effective workspace entitlements (Plan + Quota + Period meters).
        Cached for 60 seconds to minimize database overhead under high traffic.
        """
        now = time.time()
        if use_cache and workspace_id in _ENTITLEMENT_CACHE:
            ts, cached_data = _ENTITLEMENT_CACHE[workspace_id]
            if now - ts < CACHE_TTL_SECONDS:
                return cached_data

        # 1. Resolve Workspace and Tenant
        workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")

        # 2. Resolve Active Subscription and Plan
        plan = None
        subscription = db.query(Subscription).filter(
            Subscription.tenant_id == workspace.tenant_id,
            Subscription.status == "active"
        ).first()

        if subscription:
            plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()

        if not plan:
            # Fallback to default FREE plan
            plan = PlanService.get_plan_by_id(db, "free")
            if not plan:
                PlanService.seed_plans(db)
                plan = PlanService.get_plan_by_id(db, "free")

        # 3. Resolve Current Period and Usage Counter
        current_dt = datetime.now(timezone.utc)
        period = current_dt.strftime("%Y-%m")

        counter = db.query(UsageCounter).filter(
            UsageCounter.workspace_id == workspace_id,
            UsageCounter.period == period,
            UsageCounter.metric == "videos_rendered"
        ).first()
        used_count = counter.count if counter else 0

        # Calculate reset timestamp (1st of next month)
        if current_dt.month == 12:
            next_month = current_dt.replace(year=current_dt.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            next_month = current_dt.replace(month=current_dt.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)

        remaining = max(0, plan.monthly_video_quota - used_count)

        entitlements_data = {
            "workspace_id": workspace_id,
            "tenant_id": workspace.tenant_id,
            "plan_id": plan.id,
            "plan_name": plan.name,
            "monthly_quota": plan.monthly_video_quota,
            "used_this_period": used_count,
            "remaining_quota": remaining,
            "is_quota_exhausted": remaining <= 0,
            "max_duration_seconds": plan.max_duration_seconds,
            "resolution": plan.resolution,
            "watermark": plan.watermark,
            "allowed_voices_count": plan.allowed_voices_count,
            "allowed_channels_count": plan.allowed_channels_count,
            "features": plan.features or [],
            "period": period,
            "resets_at": next_month.isoformat() + "Z"
        }

        # Update cache
        _ENTITLEMENT_CACHE[workspace_id] = (now, entitlements_data)
        return entitlements_data

    @staticmethod
    def invalidate_cache(workspace_id: str):
        """Invalidates workspace cache upon plan or quota update."""
        if workspace_id in _ENTITLEMENT_CACHE:
            del _ENTITLEMENT_CACHE[workspace_id]

    @staticmethod
    def consume_video_quota(db: Session, workspace_id: str) -> Dict[str, Any]:
        """
        ATOMIC QUOTA CONSUMPTION (Spec Section 4 & 15.4)
        Uses single conditional UPDATE ... WHERE count < limit to guarantee
        zero race conditions under parallel requests.
        """
        # Fetch uncached entitlements for strict limit
        entitlements = EntitlementService.get_effective_entitlements(db, workspace_id, use_cache=False)
        limit = entitlements["monthly_quota"]
        period = datetime.now(timezone.utc).strftime("%Y-%m")

        # 1. Ensure counter row exists
        existing = db.query(UsageCounter).filter(
            UsageCounter.workspace_id == workspace_id,
            UsageCounter.period == period,
            UsageCounter.metric == "videos_rendered"
        ).first()

        if not existing:
            counter_id = str(uuid.uuid4())
            try:
                db.execute(
                    text("""
                        INSERT INTO usage_counters (id, workspace_id, period, metric, count, updated_at)
                        VALUES (:id, :workspace_id, :period, 'videos_rendered', 0, NOW())
                    """),
                    {"id": counter_id, "workspace_id": workspace_id, "period": period}
                )
                db.commit()
            except Exception:
                db.rollback()

        # 2. Atomic increment with WHERE count < limit
        result = db.execute(
            text("""
                UPDATE usage_counters
                SET count = count + 1, updated_at = NOW()
                WHERE workspace_id = :workspace_id
                  AND period = :period
                  AND metric = 'videos_rendered'
                  AND count < :limit
            """),
            {"workspace_id": workspace_id, "period": period, "limit": limit}
        )
        db.commit()

        # Invalidate cache
        EntitlementService.invalidate_cache(workspace_id)

        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "MONTHLY_QUOTA_EXCEEDED",
                    "message": f"You have reached your monthly limit of {limit} videos for this period.",
                    "used": limit,
                    "limit": limit,
                    "resets_at": entitlements["resets_at"]
                }
            )

        # Return updated usage
        counter = db.query(UsageCounter).filter(
            UsageCounter.workspace_id == workspace_id,
            UsageCounter.period == period,
            UsageCounter.metric == "videos_rendered"
        ).first()
        new_count = counter.count if counter else limit

        return {
            "status": "quota_consumed",
            "workspace_id": workspace_id,
            "used": new_count,
            "remaining": max(0, limit - new_count),
            "limit": limit
        }

    @staticmethod
    def require_feature(feature_name: str):
        """
        FastAPI Dependency checking if current workspace has entitlement for a feature.
        Raises 403 FEATURE_LOCKED with upgrade guidance if not permitted.
        """
        def dependency(workspace_id: str, db: Session = Depends(get_db)):
            entitlements = EntitlementService.get_effective_entitlements(db, workspace_id)
            allowed_features = entitlements.get("features", [])
            
            # Map shorthand aliases
            feature_aliases = {
                "publish": "single_channel_auto_dispatch",
                "direct_dispatch": "single_channel_auto_dispatch",
                "multi_channel": "multi_channel_auto_dispatch",
                "character_mode": "character_mode",
                "brand_voice": "custom_brand_voice"
            }
            required = feature_aliases.get(feature_name, feature_name)

            # Check if required feature is present in plan features
            has_access = (
                required in allowed_features or
                "all_modes" in allowed_features or
                "all_modes_+_performance_autopilot" in [f.lower().replace(" ", "_") for f in allowed_features]
            )

            if not has_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "FEATURE_LOCKED",
                        "feature": feature_name,
                        "current_plan": entitlements["plan_id"],
                        "message": f"Feature '{feature_name}' is locked on the {entitlements['plan_name']}. Please upgrade to access this feature."
                    }
                )
            return entitlements
        return dependency
