import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    channels = relationship("Channel", back_populates="owner", cascade="all, delete-orphan")
    social_accounts = relationship("SocialAccount", back_populates="owner", cascade="all, delete-orphan")
    video_projects = relationship("VideoProject", back_populates="owner", cascade="all, delete-orphan")


class Channel(Base):
    __tablename__ = "channels"

    id = Column(String(100), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    niche = Column(String(100), nullable=False)
    language = Column(String(50), default="Tamil")
    default_voice = Column(String(100), default="ta-IN-ValluvarNeural")
    avatar = Column(String(10), default="👶")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="channels")


class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id = Column(String(100), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String(50), nullable=False)  # youtube, instagram, facebook, tiktok
    account_name = Column(String(255), nullable=False)
    handle = Column(String(255), nullable=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    is_connected = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="social_accounts")


class VideoProject(Base):
    __tablename__ = "video_projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    channel_id = Column(String(100), nullable=True)
    title = Column(String(255), nullable=False)
    prompt = Column(Text, nullable=True)
    script_text = Column(Text, nullable=False)
    voice_id = Column(String(100), nullable=True)
    video_url = Column(String(500), nullable=True)
    status = Column(String(50), default="draft")  # draft, rendered, published
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="video_projects")
