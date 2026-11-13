import uuid
import json
import asyncio
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entities import RenderJob, JobStep, Workspace
from app.orchestration.pipeline import PipelineSpineOrchestrator
from app.orchestration.fair_queue import FairQueueAdmissionController
from app.services.entitlement_service import EntitlementService
from app.services.trend_radar import TrendRadarService, TrendItem
from app.services.script_engine import ScriptEngine, ReelScript
from app.services.visual_ladder import VisualLadderService
from app.services.tts_service import TTSService
from app.services.subtitle_aligner import SubtitleAlignerService
from app.services.video_composer import VideoComposerService, CompositionPlan, SceneMediaItem
from app.services.qa_gates import QAGatesService, FullQAReport

router = APIRouter(prefix="/api/v1/jobs", tags=["Pipeline Spine & Step-Ledger"])

class CompileScriptRequest(BaseModel):
    topic: str
    niche: Optional[str] = "daily_facts"
    target_duration: Optional[int] = 30
    voice_mode: Optional[str] = "solo_male"
    hook_formula: Optional[str] = "curiosity_gap"

class RealRenderRequest(BaseModel):
    workspace_id: str
    topic: str
    niche: Optional[str] = "daily_facts"
    target_duration: Optional[int] = 30
    voice_mode: Optional[str] = "solo_male"
    hook_formula: Optional[str] = "curiosity_gap"
    allow_network: Optional[bool] = False

class SubmitJobRequest(BaseModel):
    workspace_id: str
    topic: str
    niche: Optional[str] = "emotional_drama"
    language: Optional[str] = "Tamil"
    voice: Optional[str] = "ta-IN-ValluvarNeural"
    watermark: Optional[bool] = False

@router.post("/submit", status_code=status.HTTP_202_ACCEPTED)
def submit_video_job(req: SubmitJobRequest, db: Session = Depends(get_db)):
    """
    Submits a new vertical video generation job through the Step-Ledger Orchestrator.
    Enforces atomic quota check and Fair Queue admission control.
    """
    # 1. Resolve workspace & plan
    workspace = db.query(Workspace).filter(Workspace.id == req.workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    entitlements = EntitlementService.get_effective_entitlements(db, req.workspace_id)
    plan_tier = entitlements.get("plan_id", "free")
    watermark = entitlements.get("watermark", True)

    # 2. Atomic Quota Consumption (Raises 429 if limit reached)
    EntitlementService.consume_video_quota(db, req.workspace_id)

    # 3. Check Admission Control (CAP-01)
    admission = FairQueueAdmissionController.check_admission_control(db, plan_tier=plan_tier)

    # 4. Run Pipeline Orchestration
    result = PipelineSpineOrchestrator.run_pipeline(
        db=db,
        workspace_id=req.workspace_id,
        topic=req.topic,
        niche=req.niche or "emotional_drama",
        language=req.language or "Tamil",
        voice=req.voice or "ta-IN-ValluvarNeural",
        plan_tier=plan_tier,
        watermark=watermark
    )

    return {
        "status": result["status"],
        "job_id": result["job_id"],
        "degraded": result.get("degraded", False),
        "estimated_duration_sec": admission["estimated_eta_seconds"],
        "honest_eta": admission["honest_eta_human"],
        "output_video_url": result.get("output_video_url")
    }

@router.get("/{job_id}/ledger")
def get_job_step_ledger(job_id: str, db: Session = Depends(get_db)):
    """
    AutoReels v2.0 Section 4 Step-Ledger Inspector.
    Returns immutable execution history of all DAG steps, retries, input hashes, and error states.
    """
    job = db.query(RenderJob).filter(RenderJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Render job not found")

    steps = db.query(JobStep).filter(JobStep.job_id == job_id).order_by(JobStep.step_key, JobStep.scene_index).all()

    return {
        "job_id": job.id,
        "title": job.title,
        "status": job.status,
        "degraded": job.degraded,
        "current_step": job.current_step,
        "progress_percent": job.progress_percent,
        "output_video_url": job.output_video_url,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "steps": [
            {
                "id": s.id,
                "step_key": s.step_key,
                "scene_index": s.scene_index,
                "status": s.status,
                "attempt": s.attempt,
                "provider": s.provider,
                "input_hash": s.input_hash,
                "error_class": s.error_class,
                "error_detail": s.error_detail,
                "cost_micros": s.cost_micros,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "finished_at": s.finished_at.isoformat() if s.finished_at else None
            }
            for s in steps
        ]
    }

@router.post("/{job_id}/retry")
def retry_failed_job_steps(job_id: str, db: Session = Depends(get_db)):
    """
    Resumes a failed or degraded job from the first non-succeeded step.
    Succeeded steps are skipped via input_hash idempotency.
    """
    job = db.query(RenderJob).filter(RenderJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Render job not found")

    result = PipelineSpineOrchestrator.run_pipeline(
        db=db,
        workspace_id=job.workspace_id,
        topic=job.title,
        plan_tier=job.plan_tier,
        custom_job_id=job.id
    )
    return result

@router.get("/trends", response_model=List[TrendItem])
async def get_viral_trends(category: str = "all"):
    """
    Trend Radar v1 endpoint (Spec 2.2 #6).
    Returns real-time curated trends with velocity scoring and SSRF-hardened summaries.
    """
    return await TrendRadarService.fetch_curated_trends(category=category)

@router.post("/compile-script", response_model=ReelScript)
def compile_reel_script(req: CompileScriptRequest):
    """
    Script Engine & Prompt Compiler (Spec 4.1).
    Transforms topics into high-retention 3-act scripts with strict JSON schema validation.
    """
    return ScriptEngine.generate_script(
        topic=req.topic,
        niche=req.niche or "daily_facts",
        target_duration=req.target_duration or 30,
        voice_mode=req.voice_mode or "solo_male",
        hook_formula=req.hook_formula or "curiosity_gap"
    )

@router.post("/render-real")
async def execute_real_free_pipeline(req: RealRenderRequest, db: Session = Depends(get_db)):
    """
    Phase 7 Real Free Generation Pipeline (End of the video flow).
    Generates script -> multi-speaker TTS -> kinetic ASS subtitles -> visual scenes -> FFmpeg video -> QA gates.
    Strictly zero marginal cash cost (FREE-01).
    """
    # 1. Resolve workspace & entitlements
    workspace = db.query(Workspace).filter(Workspace.id == req.workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    entitlements = EntitlementService.get_effective_entitlements(db, req.workspace_id)
    plan_tier = entitlements.get("plan_id", "free")
    watermark = entitlements.get("watermark", True)
    target_w = 720 if plan_tier == "free" else 1080
    target_h = 1280 if plan_tier == "free" else 1920

    # 2. Consume quota
    EntitlementService.consume_video_quota(db, req.workspace_id)

    # 3. Compile Script
    script = ScriptEngine.generate_script(
        topic=req.topic,
        niche=req.niche or "daily_facts",
        target_duration=req.target_duration or 30,
        voice_mode=req.voice_mode or "solo_male",
        hook_formula=req.hook_formula or "curiosity_gap"
    )

    job_id = str(uuid.uuid4())
    job = RenderJob(
        id=job_id,
        workspace_id=req.workspace_id,
        title=script.title,
        status="processing",
        plan_tier=plan_tier,
        estimated_duration_sec=30,
        current_step="audio_synthesis",
        progress_percent=20
    )
    db.add(job)
    db.commit()

    # 4. Multi-Speaker Audio Synthesis
    tts_result = await TTSService.synthesize(
        text_or_blocks=script.scenes[0].narration,
        output_filename=f"job_{job_id}_tts.wav",
        allow_network=req.allow_network
    )

    # 5. Kinetic Subtitle Generation (ASS)
    chunks = SubtitleAlignerService.generate_word_alignments(tts_result.segments)
    ass_path = SubtitleAlignerService.create_ass_script(
        chunks=chunks,
        output_filename=f"job_{job_id}_captions.ass",
        video_width=target_w,
        video_height=target_h
    )

    # 6. Visual Scenes (Image Ladder)
    job.current_step = "visual_generation"
    job.progress_percent = 50
    db.commit()

    scene_items: List[SceneMediaItem] = []
    is_degraded = False
    for sc in script.scenes[:3]:  # Generate primary scenes
        vis = await VisualLadderService.generate_scene_visual(
            prompt=sc.visual_description,
            output_filename=f"job_{job_id}_scene_{sc.scene_index}.jpg",
            scene_index=sc.scene_index,
            width=target_w,
            height=target_h,
            allow_network=req.allow_network
        )
        if vis.degraded:
            is_degraded = True
        scene_items.append(SceneMediaItem(
            image_path=vis.file_path,
            duration_sec=max(1.5, tts_result.duration_sec / 3.0),
            scene_index=sc.scene_index
        ))

    # 7. Video Composition via FFmpeg
    job.current_step = "video_composition"
    job.progress_percent = 80
    db.commit()

    out_mp4_name = f"autoreels_{job_id}.mp4"
    rendered_video_path = VideoComposerService.compose_video(CompositionPlan(
        scenes=scene_items,
        audio_path=tts_result.audio_path,
        subtitle_ass_path=ass_path,
        output_filename=out_mp4_name,
        plan_tier=plan_tier,
        target_width=target_w,
        target_height=target_h,
        apply_watermark=watermark
    ))

    # 8. Automated QA Evaluation (QA-01 to QA-08)
    qa_report = QAGatesService.evaluate_video(
        video_path=rendered_video_path,
        plan_tier=plan_tier,
        is_degraded=is_degraded,
        max_duration_sec=60.0
    )

    job.status = "succeeded_degraded" if is_degraded else "completed"
    job.current_step = "finished"
    job.progress_percent = 100
    job.degraded = is_degraded
    job.output_video_path = rendered_video_path
    job.output_video_url = f"/storage/video/{out_mp4_name}"
    db.commit()

    return {
        "job_id": job.id,
        "status": job.status,
        "title": script.title,
        "degraded": is_degraded,
        "output_video_path": rendered_video_path,
        "output_video_url": job.output_video_url,
        "script": script.model_dump(),
        "qa_report": qa_report.model_dump()
    }

@router.get("/{job_id}/stream")
async def stream_job_progress(job_id: str, db: Session = Depends(get_db)):
    """
    Spec Phase 8: Live job progress over Server-Sent Events (SSE) with honest ETA.
    Streams incremental state changes, DAG steps, and heartbeat timestamps.
    """
    job = db.query(RenderJob).filter(RenderJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    async def event_generator():
        for _ in range(60):
            db.expire_all()
            current_job = db.query(RenderJob).filter(RenderJob.id == job_id).first()
            if not current_job:
                break

            steps = db.query(JobStep).filter(JobStep.job_id == job_id).all()
            steps_data = [
                {
                    "step_key": s.step_key,
                    "scene_index": s.scene_index,
                    "status": s.status,
                    "provider": s.provider,
                    "attempt": s.attempt
                }
                for s in steps
            ]

            payload = {
                "job_id": current_job.id,
                "status": current_job.status,
                "current_step": current_job.current_step,
                "progress_percent": current_job.progress_percent,
                "degraded": current_job.degraded,
                "output_video_url": current_job.output_video_url,
                "estimated_duration_sec": current_job.estimated_duration_sec,
                "steps": steps_data
            }

            yield f"data: {json.dumps(payload)}\n\n"

            if current_job.status in ("completed", "succeeded_degraded", "failed", "cancelled"):
                yield "event: complete\ndata: {}\n\n"
                break

            await asyncio.sleep(1.0)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/workspace/{workspace_id}")
def get_workspace_jobs_history(workspace_id: str, limit: int = 20, db: Session = Depends(get_db)):
    """
    Spec Phase 8: Returns history of rendered reels for the workspace.
    """
    jobs = db.query(RenderJob).filter(
        RenderJob.workspace_id == workspace_id
    ).order_by(RenderJob.created_at.desc()).limit(limit).all()

    return [
        {
            "id": j.id,
            "title": j.title,
            "status": j.status,
            "degraded": j.degraded,
            "output_video_url": j.output_video_url,
            "plan_tier": j.plan_tier,
            "estimated_duration_sec": j.estimated_duration_sec,
            "created_at": j.created_at.isoformat() if j.created_at else None
        }
        for j in jobs
    ]
