import os
import time
import uuid
import logging
import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.config.settings import settings
from app.database import engine, Base, check_db_connection
from app.models.entities import User, Channel, SocialAccount, VideoProject
from app.api.auth import router as auth_router, get_current_user
from app.services.voice_service import VoiceService
from app.services.media_service import MediaService
from app.services.script_service import ScriptService
from app.services.render_service import RenderService
from app.services.social_service import SocialDispatcher

# Configure structured logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'
)
logger = logging.getLogger("autoreels.api")

# Ensure database tables exist
Base.metadata.create_all(bind=engine)

# Unified storage setup
STORAGE_DIR = settings.STORAGE_LOCAL_DIR
for sub in ["audio", "images", "video", "output"]:
    os.makedirs(os.path.join(STORAGE_DIR, sub), exist_ok=True)

app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise Short-Form Video Automation Engine (Master Build Specification v2.0 / Free-First)",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID & Observability Middleware
@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    start_time = time.time()
    
    # Store request id in request state
    request.state.request_id = request_id
    
    response: Response = await call_next(request)
    
    duration_ms = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    
    # Structured audit log entry
    log_data = {
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": duration_ms,
        "client_ip": request.client.host if request.client else "unknown"
    }
    logger.info(json.dumps(log_data))
    return response

# Mount local storage directory for static assets
app.mount("/storage", StaticFiles(directory=STORAGE_DIR), name="storage")

# Register Auth router
app.include_router(auth_router)

dispatcher = SocialDispatcher()

# Request schemas
class ScriptRequest(BaseModel):
    topic: str
    niche: str = "emotional_drama"
    language: str = "Tamil"

class VoiceRequest(BaseModel):
    text: str
    voice: str = "ta-IN-ValluvarNeural"
    filename: Optional[str] = "speech.mp3"

class SceneImageRequest(BaseModel):
    prompt: str
    scene_id: int
    filename: Optional[str] = None

class RenderRequest(BaseModel):
    scene_images: List[str]
    audio_path: str
    srt_path: Optional[str] = None
    output_filename: str = "final_reel.mp4"
    watermark: bool = False

class PublishRequest(BaseModel):
    account_ids: List[str]
    video_path: str
    title: str
    description: str
    tags: List[str]

# Health Probes (Spec Section 10 & 14)
@app.get("/health/live")
def health_liveness():
    """Liveness probe: verifies the process is running and responsive."""
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "spec_version": settings.SPEC_VERSION
    }

@app.get("/health/ready")
def health_readiness():
    """Readiness probe: validates database connectivity, storage writeability, and worker components."""
    db_ok = check_db_connection()
    
    # Check storage writeability
    storage_ok = False
    try:
        test_file = os.path.join(STORAGE_DIR, ".health_check_write")
        with open(test_file, "w") as f:
            f.write("ok")
        if os.path.exists(test_file):
            os.remove(test_file)
            storage_ok = True
    except Exception as ex:
        logger.error(f"Storage health check failed: {ex}")
        storage_ok = False
        
    overall_status = "ready" if (db_ok and storage_ok) else "degraded"
    status_code = 200 if overall_status == "ready" else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": overall_status,
            "database": "connected" if db_ok else "unreachable",
            "storage": "writable" if storage_ok else "read_only_or_failed",
            "database_url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "local",
            "environment": settings.ENV,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

@app.get("/")
def root_info():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "spec": settings.SPEC_VERSION,
        "status": "online",
        "endpoints": {
            "liveness": "/health/live",
            "readiness": "/health/ready",
            "plans": "/api/plans",
            "auth": "/api/auth",
            "voices": "/api/voices",
            "docs": "/docs" if settings.DEBUG else "disabled"
        }
    }

@app.get("/api/plans")
def get_plans():
    """AutoReels v2.0 Section 15.4 Plan Matrix"""
    return [
        {
            "id": "free",
            "name": "Free Tier",
            "max_duration_sec": 30,
            "resolution": "720x1280",
            "watermark": True,
            "voices": 2,
            "social_channels": 0,
            "modes": ["Zero-Input (Preset Niches)"],
            "storage_retention_days": 3,
            "price_monthly": "$0.00"
        },
        {
            "id": "plan_a",
            "name": "Plan A (Creator)",
            "max_duration_sec": 45,
            "resolution": "1080x1920",
            "watermark": False,
            "voices": 6,
            "social_channels": 1,
            "modes": ["Zero-Input", "Director Mode"],
            "storage_retention_days": 14,
            "price_monthly": "$9.00 / Free Promo"
        },
        {
            "id": "plan_b",
            "name": "Plan B (Growth)",
            "max_duration_sec": 60,
            "resolution": "1080x1920",
            "watermark": False,
            "voices": 12,
            "social_channels": 3,
            "modes": ["Zero-Input", "Director Mode", "Character Mode"],
            "storage_retention_days": 30,
            "price_monthly": "$29.00"
        },
        {
            "id": "plan_c",
            "name": "Plan C (Agency / Enterprise)",
            "max_duration_sec": 60,
            "resolution": "1080x1920",
            "watermark": False,
            "voices": "All + Brand Voice",
            "social_channels": 10,
            "modes": ["All Modes + Performance Autopilot"],
            "storage_retention_days": 60,
            "price_monthly": "$79.00"
        }
    ]

@app.get("/api/voices")
def get_voices():
    return VoiceService.get_supported_voices()

@app.post("/api/script/blueprint")
def generate_blueprint(req: ScriptRequest):
    return ScriptService.generate_story_blueprint(
        topic=req.topic,
        niche=req.niche,
        language=req.language
    )

@app.post("/api/voice/synthesize")
async def synthesize_voice(req: VoiceRequest):
    out_path = os.path.join(STORAGE_DIR, "audio", req.filename)
    result = await VoiceService.generate_speech_with_subtitles(
        text=req.text,
        voice=req.voice,
        output_audio_path=out_path
    )
    result["url"] = f"http://localhost:8000/storage/audio/{req.filename}"
    return result

@app.post("/api/media/generate-scene")
async def generate_scene_image(req: SceneImageRequest):
    filename = req.filename or f"scene_{req.scene_id}_{int(os.times().system)}.jpg"
    img_path = await MediaService.generate_ai_image(
        prompt=req.prompt,
        output_filename=filename
    )
    return {
        "scene_id": req.scene_id,
        "image_path": img_path,
        "url": f"http://localhost:8000/storage/images/{filename}"
    }

@app.post("/api/render/video")
def render_video(req: RenderRequest):
    try:
        audio_full_path = req.audio_path
        if not os.path.isabs(audio_full_path):
            audio_full_path = os.path.join(STORAGE_DIR, "audio", os.path.basename(req.audio_path))

        real_image_paths = []
        for img in req.scene_images:
            if not os.path.isabs(img):
                img = os.path.join(STORAGE_DIR, "images", os.path.basename(img))
            if os.path.exists(img):
                real_image_paths.append(img)

        if not real_image_paths:
            fallback_img = os.path.join(STORAGE_DIR, "images", "fallback.jpg")
            real_image_paths = [fallback_img] if os.path.exists(fallback_img) else req.scene_images

        rendered_path = RenderService.render_reel(
            scene_image_paths=real_image_paths,
            audio_path=audio_full_path,
            srt_path=req.srt_path,
            output_filename=req.output_filename,
            watermark=req.watermark
        )
        return {
            "status": "success",
            "video_path": rendered_path,
            "url": f"http://localhost:8000/storage/output/{req.output_filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/accounts")
def list_accounts():
    return dispatcher.get_connected_accounts()

@app.post("/api/social/publish")
def publish_to_accounts(req: PublishRequest):
    results = dispatcher.broadcast_to_selected_accounts(
        account_ids=req.account_ids,
        video_path=req.video_path,
        title=req.title,
        description=req.description,
        tags=req.tags
    )
    return {
        "status": "published_batch",
        "results": results
    }
