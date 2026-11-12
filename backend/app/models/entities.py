import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, BigInteger
)
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

# ==========================================
# 1. TENANCY & WORKSPACE HIERARCHY
# ==========================================

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    workspaces = relationship("Workspace", back_populates="tenant", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="tenant", uselist=False, cascade="all, delete-orphan")
    plan_change_requests = relationship("PlanChangeRequest", back_populates="tenant", cascade="all, delete-orphan")


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    is_default = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    tenant = relationship("Tenant", back_populates="workspaces")
    memberships = relationship("Membership", back_populates="workspace", cascade="all, delete-orphan")
    usage_counters = relationship("UsageCounter", back_populates="workspace", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="workspace", cascade="all, delete-orphan")
    render_jobs = relationship("RenderJob", back_populates="workspace", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    memberships = relationship("Membership", back_populates="user", cascade="all, delete-orphan")
    channels = relationship("Channel", back_populates="owner", cascade="all, delete-orphan")
    social_accounts = relationship("SocialAccount", back_populates="owner", cascade="all, delete-orphan")
    video_projects = relationship("VideoProject", back_populates="owner", cascade="all, delete-orphan")


class Membership(Base):
    __tablename__ = "memberships"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), default="OWNER")  # OWNER, ADMIN, MEMBER, VIEWER
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    workspace = relationship("Workspace", back_populates="memberships")
    user = relationship("User", back_populates="memberships")


# ==========================================
# 2. PLANS & SUBSCRIPTIONS (Spec 15.4)
# ==========================================

class Plan(Base):
    __tablename__ = "plans"

    id = Column(String(50), primary_key=True)  # free, plan_a, plan_b, plan_c
    name = Column(String(100), nullable=False)
    monthly_price_cents = Column(Integer, default=0)
    monthly_video_quota = Column(Integer, default=2)
    max_duration_seconds = Column(Integer, default=30)
    resolution = Column(String(20), default="720x1280")
    watermark = Column(Boolean, default=True)
    allowed_voices_count = Column(Integer, default=2)
    allowed_channels_count = Column(Integer, default=0)
    storage_retention_days = Column(Integer, default=3)
    is_active = Column(Boolean, default=True)
    features = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), unique=True, nullable=False)
    plan_id = Column(String(50), ForeignKey("plans.id"), nullable=False)
    status = Column(String(50), default="active")  # active, past_due, canceled
    current_period_start = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    current_period_end = Column(DateTime, nullable=True)

    tenant = relationship("Tenant", back_populates="subscription")
    plan = relationship("Plan", back_populates="subscriptions")


class UsageCounter(Base):
    __tablename__ = "usage_counters"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    period = Column(String(7), nullable=False, index=True)  # YYYY-MM (e.g., 2026-11)
    metric = Column(String(50), default="videos_rendered")  # videos_rendered, storage_bytes
    count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    workspace = relationship("Workspace", back_populates="usage_counters")


class PlanChangeRequest(Base):
    __tablename__ = "plan_change_requests"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    requested_plan_id = Column(String(50), ForeignKey("plans.id"), nullable=False)
    status = Column(String(50), default="pending")  # pending, approved, rejected
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    tenant = relationship("Tenant", back_populates="plan_change_requests")


# ==========================================
# 3. PLATFORM ADMIN & GOVERNANCE
# ==========================================

class PlatformAdmin(Base):
    __tablename__ = "platform_admins"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    role = Column(String(50), default="super_admin")  # super_admin, support
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String(100), primary_key=True)
    value = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class FeatureFlag(Base):
    __tablename__ = "feature_flags"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    flag_name = Column(String(100), unique=True, index=True, nullable=False)
    is_enabled = Column(Boolean, default=True)
    target_plans = Column(JSON, default=list)


# ==========================================
# 4. ASSETS & PIPELINE EXECUTION
# ==========================================

class Asset(Base):
    __tablename__ = "assets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_type = Column(String(50), nullable=False)  # image, audio, video
    storage_key = Column(String(500), nullable=False)
    url = Column(String(500), nullable=False)
    size_bytes = Column(BigInteger, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    workspace = relationship("Workspace", back_populates="assets")


class RenderJob(Base):
    __tablename__ = "render_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("video_projects.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), default="queued")  # queued, processing, completed, failed
    progress_percent = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    output_video_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    workspace = relationship("Workspace", back_populates="render_jobs")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), nullable=True, index=True)
    workspace_id = Column(String(36), nullable=True, index=True)
    user_id = Column(String(36), nullable=True)
    action = Column(String(100), nullable=False)  # e.g., video.create, plan.upgrade_request
    resource = Column(String(100), nullable=False)
    details = Column(JSON, default=dict)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ==========================================
# 5. CORE WORKSPACE ASSETS (CHANNELS & PROJECTS)
# ==========================================

class Channel(Base):
    __tablename__ = "channels"

    id = Column(String(100), primary_key=True, index=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    niche = Column(String(100), nullable=False)
    language = Column(String(50), default="Tamil")
    default_voice = Column(String(100), default="ta-IN-ValluvarNeural")
    avatar = Column(String(10), default="👶")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="channels")


class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id = Column(String(100), primary_key=True, index=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String(50), nullable=False)
    account_name = Column(String(255), nullable=False)
    handle = Column(String(255), nullable=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    is_connected = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="social_accounts")


class VideoProject(Base):
    __tablename__ = "video_projects"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    channel_id = Column(String(100), nullable=True)
    title = Column(String(255), nullable=False)
    prompt = Column(Text, nullable=True)
    script_text = Column(Text, nullable=False)
    voice_id = Column(String(100), nullable=True)
    video_url = Column(String(500), nullable=True)
    status = Column(String(50), default="draft")  # draft, rendered, published
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="video_projects")
