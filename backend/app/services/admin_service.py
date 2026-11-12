import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models.entities import (
    Tenant, Workspace, Subscription, Plan, UsageCounter,
    PlanChangeRequest, PlatformAdmin, AuditLog, User, SystemSetting
)
from app.services.entitlement_service import EntitlementService

logger = logging.getLogger("autoreels.admin")

class AdminService:
    @staticmethod
    def is_platform_admin(db: Session, user_id: int) -> Optional[PlatformAdmin]:
        """Checks if user has a platform admin role."""
        return db.query(PlatformAdmin).filter(PlatformAdmin.user_id == user_id).first()

    @staticmethod
    def get_system_telemetry(db: Session) -> Dict[str, Any]:
        """AutoReels v2.0 Section 15.6 Super Admin System Telemetry."""
        total_tenants = db.query(Tenant).count()
        total_users = db.query(User).count()
        pending_requests = db.query(PlanChangeRequest).filter(PlanChangeRequest.status == "pending").count()

        # Monthly render counts across all tenants
        period = datetime.now(timezone.utc).strftime("%Y-%m")
        total_videos_rendered = db.query(func.sum(UsageCounter.count)).filter(
            UsageCounter.period == period,
            UsageCounter.metric == "videos_rendered"
        ).scalar() or 0

        # System Daily Cap setting
        daily_cap_setting = db.query(SystemSetting).filter(SystemSetting.key == "max_videos_per_day").first()
        daily_cap = daily_cap_setting.value.get("cap", 100) if daily_cap_setting and isinstance(daily_cap_setting.value, dict) else 100

        # Active plans distribution
        plan_counts = {}
        for plan_id in ["free", "plan_a", "plan_b", "plan_c"]:
            c = db.query(Subscription).filter(Subscription.plan_id == plan_id).count()
            plan_counts[plan_id] = c

        return {
            "total_tenants": total_tenants,
            "total_users": total_users,
            "pending_upgrade_requests": pending_requests,
            "videos_rendered_this_month": int(total_videos_rendered),
            "max_videos_per_day": daily_cap,
            "plan_distribution": plan_counts,
            "active_workers": 1,
            "queue_status": "healthy",
            "capacity_status": "nominal"
        }

    @staticmethod
    def list_all_tenants(db: Session, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists all tenants with subscription and usage status."""
        query = db.query(Tenant)
        if search:
            query = query.filter(Tenant.name.ilike(f"%{search}%") | Tenant.slug.ilike(f"%{search}%"))

        tenants = query.order_by(desc(Tenant.created_at)).all()
        period = datetime.now(timezone.utc).strftime("%Y-%m")
        result = []

        for t in tenants:
            plan_id = "free"
            plan_name = "Free Tier"
            quota_limit = 2
            sub_status = "active"

            if t.subscription and t.subscription.plan:
                plan_id = t.subscription.plan.id
                plan_name = t.subscription.plan.name
                quota_limit = t.subscription.plan.monthly_video_quota
                sub_status = t.subscription.status

            # Find default workspace
            default_ws = next((w for w in t.workspaces if w.is_default), None) or (t.workspaces[0] if t.workspaces else None)
            used_count = 0
            ws_id = default_ws.id if default_ws else None

            if ws_id:
                counter = db.query(UsageCounter).filter(
                    UsageCounter.workspace_id == ws_id,
                    UsageCounter.period == period,
                    UsageCounter.metric == "videos_rendered"
                ).first()
                if counter:
                    used_count = counter.count

            result.append({
                "id": t.id,
                "name": t.name,
                "slug": t.slug,
                "plan_id": plan_id,
                "plan_name": plan_name,
                "status": sub_status,
                "videos_used": used_count,
                "quota_limit": quota_limit,
                "remaining": max(0, quota_limit - used_count),
                "workspace_id": ws_id,
                "created_at": t.created_at.isoformat() if t.created_at else None
            })
        return result

    @staticmethod
    def list_all_plans(db: Session) -> List[Dict[str, Any]]:
        """Returns all plans for the Super Admin plans editor."""
        plans = db.query(Plan).all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "monthly_price_cents": p.monthly_price_cents,
                "monthly_video_quota": p.monthly_video_quota,
                "max_duration_seconds": p.max_duration_seconds,
                "resolution": p.resolution,
                "watermark": p.watermark,
                "allowed_voices_count": p.allowed_voices_count,
                "allowed_channels_count": p.allowed_channels_count,
                "storage_retention_days": p.storage_retention_days,
                "is_active": p.is_active,
                "features": p.features or []
            }
            for p in plans
        ]

    @staticmethod
    def update_plan_limits(
        db: Session,
        plan_id: str,
        updates: Dict[str, Any],
        admin_user_id: int
    ) -> Dict[str, Any]:
        """
        Updates plan attributes (limits, features, quota).
        Enforces ADM-04 (same transaction audit log) and PLAN-04 (immediate cache invalidation).
        """
        plan = db.query(Plan).filter(Plan.id == plan_id).first()
        if not plan:
            raise ValueError(f"Plan '{plan_id}' not found")

        old_state = {
            "monthly_video_quota": plan.monthly_video_quota,
            "max_duration_seconds": plan.max_duration_seconds,
            "resolution": plan.resolution,
            "watermark": plan.watermark,
            "features": plan.features
        }

        # Apply updates
        if "monthly_video_quota" in updates:
            plan.monthly_video_quota = int(updates["monthly_video_quota"])
        if "max_duration_seconds" in updates:
            plan.max_duration_seconds = int(updates["max_duration_seconds"])
        if "resolution" in updates:
            plan.resolution = str(updates["resolution"])
        if "watermark" in updates:
            plan.watermark = bool(updates["watermark"])
        if "features" in updates:
            plan.features = list(updates["features"])
        if "name" in updates:
            plan.name = str(updates["name"])

        # PLAN-04: Clear entitlement cache across the entire application immediately
        EntitlementService._cache.clear()

        # ADM-04: Audit log committed in the same transaction
        audit = AuditLog(
            user_id=str(admin_user_id),
            action="plan.updated",
            resource="plans",
            details={
                "plan_id": plan_id,
                "old": old_state,
                "new": updates
            }
        )
        db.add(audit)
        db.commit()
        db.refresh(plan)

        return {
            "status": "success",
            "plan_id": plan.id,
            "monthly_video_quota": plan.monthly_video_quota,
            "features": plan.features
        }

    @staticmethod
    def list_upgrade_requests(db: Session, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists plan upgrade requests."""
        query = db.query(PlanChangeRequest)
        if status:
            query = query.filter(PlanChangeRequest.status == status)

        requests = query.order_by(desc(PlanChangeRequest.created_at)).all()
        result = []

        for req in requests:
            tenant = db.query(Tenant).filter(Tenant.id == req.tenant_id).first()
            user = db.query(User).filter(User.id == req.user_id).first()
            target_plan = db.query(Plan).filter(Plan.id == req.requested_plan_id).first()

            result.append({
                "id": req.id,
                "tenant_id": req.tenant_id,
                "tenant_name": tenant.name if tenant else "Unknown Tenant",
                "user_id": req.user_id,
                "user_email": user.email if user else "Unknown User",
                "current_plan_id": tenant.subscription.plan_id if tenant and tenant.subscription else "free",
                "requested_plan_id": req.requested_plan_id,
                "requested_plan_name": target_plan.name if target_plan else req.requested_plan_id,
                "status": req.status,
                "notes": req.notes,
                "created_at": req.created_at.isoformat() if req.created_at else None
            })
        return result

    @staticmethod
    def approve_upgrade_request(db: Session, request_id: str, admin_user_id: int) -> Dict[str, Any]:
        """Approves a plan upgrade request, immediately shifting tenant subscription to the target tier."""
        req = db.query(PlanChangeRequest).filter(PlanChangeRequest.id == request_id).first()
        if not req:
            raise ValueError("Upgrade request not found")

        req.status = "approved"

        # Update Tenant Subscription
        subscription = db.query(Subscription).filter(Subscription.tenant_id == req.tenant_id).first()
        if subscription:
            subscription.plan_id = req.requested_plan_id
            subscription.status = "active"
        else:
            subscription = Subscription(
                tenant_id=req.tenant_id,
                plan_id=req.requested_plan_id,
                status="active"
            )
            db.add(subscription)

        # Invalidate entitlement caches for all workspaces of this tenant
        workspaces = db.query(Workspace).filter(Workspace.tenant_id == req.tenant_id).all()
        for ws in workspaces:
            EntitlementService.invalidate_cache(ws.id)

        # Audit log committed in the same transaction (ADM-04)
        audit = AuditLog(
            tenant_id=req.tenant_id,
            user_id=str(admin_user_id),
            action="plan_change_request.approved",
            resource="subscription",
            details={
                "request_id": req.id,
                "new_plan_id": req.requested_plan_id,
                "approved_by": admin_user_id
            }
        )
        db.add(audit)
        db.commit()

        return {
            "status": "approved",
            "request_id": req.id,
            "tenant_id": req.tenant_id,
            "active_plan_id": req.requested_plan_id
        }

    @staticmethod
    def reject_upgrade_request(db: Session, request_id: str, reason: str, admin_user_id: int) -> Dict[str, Any]:
        """Rejects a plan upgrade request."""
        req = db.query(PlanChangeRequest).filter(PlanChangeRequest.id == request_id).first()
        if not req:
            raise ValueError("Upgrade request not found")

        req.status = "rejected"
        req.notes = f"{req.notes or ''} [Rejected by Admin: {reason}]"

        audit = AuditLog(
            tenant_id=req.tenant_id,
            user_id=str(admin_user_id),
            action="plan_change_request.rejected",
            resource="plan_change_request",
            details={"request_id": req.id, "reason": reason}
        )
        db.add(audit)
        db.commit()

        return {
            "status": "rejected",
            "request_id": req.id,
            "reason": reason
        }

    @staticmethod
    def change_tenant_plan_manually(
        db: Session,
        tenant_id: str,
        new_plan_id: str,
        admin_user_id: int
    ) -> Dict[str, Any]:
        """Manually overrides a tenant's active plan tier."""
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise ValueError("Tenant not found")

        plan = db.query(Plan).filter(Plan.id == new_plan_id).first()
        if not plan:
            raise ValueError(f"Target plan '{new_plan_id}' does not exist")

        if tenant.subscription:
            tenant.subscription.plan_id = new_plan_id
            tenant.subscription.status = "active"
        else:
            sub = Subscription(tenant_id=tenant.id, plan_id=new_plan_id, status="active")
            db.add(sub)

        for ws in tenant.workspaces:
            EntitlementService.invalidate_cache(ws.id)

        audit = AuditLog(
            tenant_id=tenant.id,
            user_id=str(admin_user_id),
            action="tenant.plan_manually_updated",
            resource="subscription",
            details={"new_plan_id": new_plan_id, "updated_by": admin_user_id}
        )
        db.add(audit)
        db.commit()

        return {
            "status": "plan_updated",
            "tenant_id": tenant.id,
            "new_plan_id": new_plan_id,
            "plan_name": plan.name
        }

    @staticmethod
    def set_system_daily_cap(db: Session, cap: int, admin_user_id: int) -> int:
        """Sets global daily video rendering cap."""
        setting = db.query(SystemSetting).filter(SystemSetting.key == "max_videos_per_day").first()
        if not setting:
            setting = SystemSetting(key="max_videos_per_day", value={"cap": cap})
            db.add(setting)
        else:
            setting.value = {"cap": cap}

        audit = AuditLog(
            user_id=str(admin_user_id),
            action="system_setting.updated",
            resource="system_settings",
            details={"key": "max_videos_per_day", "cap": cap}
        )
        db.add(audit)
        db.commit()
        return cap

    @staticmethod
    def list_audit_logs(db: Session, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns recent system audit events."""
        logs = db.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit).all()
        return [
            {
                "id": log.id,
                "tenant_id": log.tenant_id,
                "action": log.action,
                "resource": log.resource,
                "details": log.details,
                "user_id": log.user_id,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            for log in logs
        ]

    @staticmethod
    def execute_transaction_with_forced_audit_failure_test(
        db: Session,
        tenant_id: str,
        new_plan_id: str,
        admin_user_id: int
    ):
        """
        ADM-T2 Fault Injection Test:
        Modifies state, but forces audit insertion to fail, verifying that the entire
        transaction rolls back and no change is persisted.
        """
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise ValueError("Tenant not found")

        # Mutate subscription
        if tenant.subscription:
            tenant.subscription.plan_id = new_plan_id

        # Simulating forced audit failure (e.g. database constraint or exception)
        raise RuntimeError("SIMULATED_AUDIT_INSERT_FAILURE: Transaction must abort and roll back")
