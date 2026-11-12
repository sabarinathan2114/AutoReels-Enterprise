import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.entities import (
    Tenant, Workspace, Membership, User, Subscription, Plan, UsageCounter,
    PlanChangeRequest, Asset, VideoProject, AuditLog
)

class TenantService:
    @staticmethod
    def create_tenant_hierarchy(
        db: Session,
        user_id: int,
        tenant_name: str,
        plan_id: str = "free"
    ) -> Dict[str, Any]:
        """
        Creates Tenant, Default Workspace, Owner Membership, and Free Subscription in ONE atomic transaction.
        """
        slug = f"{tenant_name.lower().replace(' ', '-')[:30]}-{uuid.uuid4().hex[:6]}"
        tenant = Tenant(
            name=tenant_name,
            slug=slug
        )
        db.add(tenant)
        db.flush()

        # Create default workspace
        workspace = Workspace(
            tenant_id=tenant.id,
            name=f"{tenant_name}'s Workspace",
            is_default=True
        )
        db.add(workspace)
        db.flush()

        # Create OWNER membership
        membership = Membership(
            workspace_id=workspace.id,
            user_id=user_id,
            role="OWNER"
        )
        db.add(membership)

        # Create active subscription on chosen plan (defaults to 'free')
        subscription = Subscription(
            tenant_id=tenant.id,
            plan_id=plan_id,
            status="active"
        )
        db.add(subscription)

        # Audit log creation
        audit = AuditLog(
            tenant_id=tenant.id,
            workspace_id=workspace.id,
            user_id=str(user_id),
            action="tenant.provisioned",
            resource="tenant",
            details={"tenant_name": tenant_name, "plan": plan_id}
        )
        db.add(audit)

        db.commit()
        db.refresh(tenant)
        db.refresh(workspace)

        return {
            "tenant_id": tenant.id,
            "tenant_name": tenant.name,
            "workspace_id": workspace.id,
            "workspace_name": workspace.name,
            "role": membership.role,
            "plan_id": subscription.plan_id
        }

    @staticmethod
    def get_user_workspaces(db: Session, user_id: int) -> List[Workspace]:
        """Returns all workspaces where user is an active member."""
        return (
            db.query(Workspace)
            .join(Membership, Membership.workspace_id == Workspace.id)
            .filter(Membership.user_id == user_id)
            .all()
        )

    @staticmethod
    def verify_workspace_access(
        db: Session,
        user_id: int,
        workspace_id: str,
        required_role: Optional[str] = None
    ) -> bool:
        """Verifies if user has legitimate access to the workspace (and meets required role if any)."""
        membership = (
            db.query(Membership)
            .filter(
                and_(
                    Membership.user_id == user_id,
                    Membership.workspace_id == workspace_id
                )
            )
            .first()
        )
        if not membership:
            return False
        if required_role == "OWNER" and membership.role != "OWNER":
            return False
        if required_role == "ADMIN" and membership.role not in ["OWNER", "ADMIN"]:
            return False
        return True

    @staticmethod
    def get_scoped_assets(db: Session, workspace_id: str) -> List[Asset]:
        """Strictly tenant-scoped asset query (Row-Level Security equivalent in MySQL)."""
        return db.query(Asset).filter(Asset.workspace_id == workspace_id).all()

    @staticmethod
    def get_scoped_projects(db: Session, workspace_id: str) -> List[VideoProject]:
        """Strictly tenant-scoped video projects query."""
        return db.query(VideoProject).filter(VideoProject.workspace_id == workspace_id).all()

    @staticmethod
    def get_current_period_quota_usage(
        db: Session,
        workspace_id: str,
        metric: str = "videos_rendered"
    ) -> int:
        """Retrieves usage counter for current calendar month."""
        period = datetime.now(timezone.utc).strftime("%Y-%m")
        counter = (
            db.query(UsageCounter)
            .filter(
                and_(
                    UsageCounter.workspace_id == workspace_id,
                    UsageCounter.period == period,
                    UsageCounter.metric == metric
                )
            )
            .first()
        )
        return counter.count if counter else 0

    @staticmethod
    def increment_quota_usage(
        db: Session,
        workspace_id: str,
        metric: str = "videos_rendered",
        amount: int = 1
    ) -> int:
        """Atomically increments workspace quota counter."""
        period = datetime.now(timezone.utc).strftime("%Y-%m")
        counter = (
            db.query(UsageCounter)
            .filter(
                and_(
                    UsageCounter.workspace_id == workspace_id,
                    UsageCounter.period == period,
                    UsageCounter.metric == metric
                )
            )
            .first()
        )
        if not counter:
            counter = UsageCounter(
                workspace_id=workspace_id,
                period=period,
                metric=metric,
                count=amount
            )
            db.add(counter)
        else:
            counter.count += amount
        db.commit()
        db.refresh(counter)
        return counter.count
