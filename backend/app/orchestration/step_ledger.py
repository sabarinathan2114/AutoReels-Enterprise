import hashlib
import json
import time
import random
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Callable
from sqlalchemy.orm import Session

from app.models.entities import JobStep, RenderJob
from app.orchestration.errors import ErrorClass, StepExecutionError, classify_exception
from app.orchestration.provider_router import ProviderRouter
from app.services.entitlement_service import EntitlementService

logger = logging.getLogger("autoreels.step_ledger")

def compute_input_hash(step_key: str, params: Dict[str, Any]) -> str:
    """
    AutoReels v2.0 Section 4.3 Content-Addressable Input Hash.
    sha256(step_key + sorted_json_params)
    """
    serialized = json.dumps(params, sort_keys=True, default=str)
    raw = f"{step_key}:{serialized}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

class StepLedgerOrchestrator:
    @staticmethod
    def execute_step(
        db: Session,
        job_id: str,
        workspace_id: str,
        step_key: str,
        scene_index: Optional[int],
        params: Dict[str, Any],
        step_executor: Callable[[str, Dict[str, Any]], Dict[str, Any]],
        plan_tier: str = "free",
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Executes a workflow step using the durable SQL Step Ledger.
        Guarantees:
        1. Idempotency: exact input_hash match on SUCCEEDED step skips execution.
        2. Partial-failure recovery: only failed scene/step re-executes.
        3. Jittered exponential backoff retries for transient errors.
        4. Provider fallback chain & circuit breaker integration.
        5. Degradation policy before DLQ.
        6. Quota refund on fatal platform failure.
        """
        input_hash = compute_input_hash(step_key, params)

        # 1. Fetch or create JobStep record
        step = db.query(JobStep).filter(
            JobStep.job_id == job_id,
            JobStep.step_key == step_key,
            JobStep.scene_index == scene_index
        ).first()

        if not step:
            step = JobStep(
                job_id=job_id,
                workspace_id=workspace_id,
                step_key=step_key,
                scene_index=scene_index,
                input_hash=input_hash,
                status="PENDING",
                attempt=0
            )
            db.add(step)
            db.commit()
            db.refresh(step)

        # IDEMPOTENCY CHECK: if already succeeded with identical input_hash, return cached result
        if step.status == "SUCCEEDED" and step.input_hash == input_hash and step.output_payload:
            logger.info(f"[IDEMPOTENT_CACHE_HIT] Skipping step {step_key} (scene {scene_index}) - output cached")
            return step.output_payload

        # Update input hash if parameters changed
        step.input_hash = input_hash
        step.status = "RUNNING"
        step.started_at = datetime.now(timezone.utc)
        step.heartbeat_at = datetime.now(timezone.utc)
        db.commit()

        # 2. Resolve Candidate Providers
        candidates = ProviderRouter.get_candidate_providers(step_key, plan_tier=plan_tier)
        if not candidates:
            # Fallback default
            candidates = [{"id": f"{step_key}_default", "cost_micros": 0}]

        last_exception: Optional[Exception] = None

        # 3. Execution Loop with Provider Fallback & Jittered Retries
        for provider_info in candidates:
            provider_id = provider_info["id"]
            step.provider = provider_id
            db.commit()

            for attempt in range(1, max_retries + 1):
                step.attempt += 1
                step.heartbeat_at = datetime.now(timezone.utc)
                db.commit()

                try:
                    # Execute Step Action
                    result = step_executor(provider_id, params)

                    # Mark Success
                    step.status = "SUCCEEDED"
                    step.finished_at = datetime.now(timezone.utc)
                    step.output_payload = result
                    step.error_class = None
                    step.error_detail = None
                    step.cost_micros = provider_info.get("cost_micros", 0)

                    ProviderRouter.record_provider_result(provider_id, success=True)
                    db.commit()
                    return result

                except Exception as ex:
                    last_exception = ex
                    err_class = classify_exception(ex)
                    step.error_class = err_class.value
                    step.error_detail = str(ex)
                    db.commit()

                    logger.warning(
                        f"Step {step_key} (scene {scene_index}) failed attempt {attempt}/{max_retries} "
                        f"on provider {provider_id} with class {err_class.value}: {ex}"
                    )

                    # Handle TRANSIENT errors with exponential backoff & jitter
                    if err_class == ErrorClass.TRANSIENT and attempt < max_retries:
                        delay = min(10.0, (1.0 * (2 ** (attempt - 1))) + random.uniform(0.1, 0.5))
                        time.sleep(delay)
                        continue
                    else:
                        # Record provider failure to circuit breaker and break to try next provider
                        ProviderRouter.record_provider_result(provider_id, success=False)
                        break

        # 4. All providers in fallback chain exhausted -> Evaluate Degradation Policy
        if step_key == "image":
            # Apply spec Section 4.2 degradation: fallback solid color or cached frame
            logger.warning(f"All image providers failed for scene {scene_index}. Applying degradation fallback.")
            degraded_payload = {
                "image_url": "/storage/images/fallback.jpg",
                "degraded": True,
                "reason": "Provider exhaustion; graceful fallback applied"
            }
            step.status = "DEGRADED"
            step.output_payload = degraded_payload
            step.finished_at = datetime.now(timezone.utc)

            # Flag job as degraded
            job = db.query(RenderJob).filter(RenderJob.id == job_id).first()
            if job:
                job.degraded = True
                job.status = "succeeded_degraded"
            db.commit()
            return degraded_payload

        # 5. Non-degradable Step Failure -> DLQ & Fatal Handling
        step.status = "FAILED"
        step.finished_at = datetime.now(timezone.utc)

        job = db.query(RenderJob).filter(RenderJob.id == job_id).first()
        if job:
            job.status = "failed"
            job.error_message = f"Step {step_key} failed: {last_exception}"

        # If platform fatal error, refund consumed quota (Spec Section 4.2)
        if step.error_class == ErrorClass.FATAL.value:
            logger.error(f"Platform fatal error on job {job_id}. Automatically refunding video quota to workspace {workspace_id}.")
            try:
                EntitlementService.refund_video_quota(db, workspace_id)
            except Exception as ref_err:
                logger.error(f"Failed to refund quota: {ref_err}")

        db.commit()
        raise StepExecutionError(
            message=f"Step {step_key} failed after exhausting fallback chain: {last_exception}",
            error_class=ErrorClass(step.error_class) if step.error_class else ErrorClass.FATAL
        )
