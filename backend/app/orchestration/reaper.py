import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.entities import JobStep, RenderJob

logger = logging.getLogger("autoreels.reaper")

class OrchestratorReaper:
    """
    AutoReels v2.0 Section 4.4 Worker Crash Safety & Reaper.
    Periodically inspects running steps and jobs that lost their heartbeat.
    Recovers orphaned tasks back to PENDING so another worker can safely pick them up.
    """
    DEFAULT_HEARTBEAT_TIMEOUT_SECONDS = 120  # 2 minutes without heartbeat

    @classmethod
    def reap_stale_steps(
        cls,
        db: Session,
        timeout_seconds: int = DEFAULT_HEARTBEAT_TIMEOUT_SECONDS
    ) -> List[Dict[str, Any]]:
        threshold = datetime.now(timezone.utc) - timedelta(seconds=timeout_seconds)

        stale_steps = db.query(JobStep).filter(
            JobStep.status == "RUNNING",
            JobStep.heartbeat_at < threshold
        ).all()

        reaped = []
        for step in stale_steps:
            logger.warning(
                f"[REAPER] Reaping stale step {step.step_key} (scene {step.scene_index}) "
                f"for job {step.job_id}. Heartbeat expired at {step.heartbeat_at}"
            )
            step.status = "PENDING"
            step.error_class = "TRANSIENT"
            step.error_detail = "Reaped after worker heartbeat timeout"
            reaped.append({
                "job_id": step.job_id,
                "step_key": step.step_key,
                "scene_index": step.scene_index,
                "status": "reset_to_pending"
            })

        stale_jobs = db.query(RenderJob).filter(
            RenderJob.status == "processing",
            RenderJob.heartbeat_at < threshold
        ).all()

        for job in stale_jobs:
            logger.warning(f"[REAPER] Resetting stale render job {job.id} to queued.")
            job.status = "queued"
            job.error_message = "Recovered by orchestrator reaper after worker crash"

        db.commit()
        return reaped
