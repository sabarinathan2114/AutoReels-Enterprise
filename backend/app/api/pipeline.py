from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entities import RenderJob, JobStep, Workspace
from app.orchestration.pipeline import PipelineSpineOrchestrator
from app.orchestration.fair_queue import FairQueueAdmissionController
from app.services.entitlement_service import EntitlementService

router = APIRouter(prefix="/api/v1/jobs", tags=["Pipeline Spine & Step-Ledger"])

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
