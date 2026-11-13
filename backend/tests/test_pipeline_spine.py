import uuid
import time
from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import SessionLocal
from app.models.entities import Tenant, Workspace, User, RenderJob, JobStep, UsageCounter, SystemSetting
from app.services.auth_service import AuthService
from app.services.tenant_service import TenantService
from app.services.entitlement_service import EntitlementService
from app.orchestration.step_ledger import StepLedgerOrchestrator, compute_input_hash
from app.orchestration.circuit_breaker import CircuitBreaker, CircuitBreakerRegistry, CircuitState
from app.orchestration.provider_router import ProviderRouter
from app.orchestration.errors import ErrorClass, StepExecutionError
from app.orchestration.reaper import OrchestratorReaper
from app.orchestration.fair_queue import FairQueueAdmissionController
from app.orchestration.pipeline import PipelineSpineOrchestrator

client = TestClient(app)

@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="module")
def setup_tenancy(db: Session):
    unique = uuid.uuid4().hex[:8]
    creator = AuthService.create_user(db, email=f"pipeline_{unique}@example.com", plain_password="Password123!")
    tenant_info = TenantService.create_tenant_hierarchy(
        db=db,
        user_id=creator.id,
        tenant_name=f"Pipeline Studio {unique}",
        plan_id="free"
    )
    token = AuthService.create_access_token({
        "sub": creator.email,
        "user_id": creator.id,
        "workspace_id": tenant_info["workspace_id"]
    })
    return {
        "user": creator,
        "tenant_id": tenant_info["tenant_id"],
        "workspace_id": tenant_info["workspace_id"],
        "token": token
    }

def test_idempotent_step_execution_skips_rerun(setup_tenancy, db: Session):
    """
    Spec Section 4.1: Steps are idempotent.
    Exact match on input_hash returns cached result; executor called only once.
    """
    ws_id = setup_tenancy["workspace_id"]
    job_id = str(uuid.uuid4())
    job = RenderJob(id=job_id, workspace_id=ws_id, title="Test Reel", status="processing")
    db.add(job)
    db.commit()

    call_count = {"count": 0}
    def mock_executor(provider: str, params: dict):
        call_count["count"] += 1
        return {"result": "generated_content_v1", "provider": provider}

    params = {"prompt": "cinematic neon cityscape", "resolution": "720x1280"}

    # Run 1: Should execute
    res1 = StepLedgerOrchestrator.execute_step(
        db=db,
        job_id=job_id,
        workspace_id=ws_id,
        step_key="image",
        scene_index=0,
        params=params,
        step_executor=mock_executor
    )
    assert res1["result"] == "generated_content_v1"
    assert call_count["count"] == 1

    # Run 2 with identical input_hash: MUST skip execution and return cached output
    res2 = StepLedgerOrchestrator.execute_step(
        db=db,
        job_id=job_id,
        workspace_id=ws_id,
        step_key="image",
        scene_index=0,
        params=params,
        step_executor=mock_executor
    )
    assert res2["result"] == "generated_content_v1"
    assert call_count["count"] == 1, "Expected cached execution: step executor should NOT be called twice!"

def test_partial_failure_retry_with_jitter(setup_tenancy, db: Session):
    """
    Spec Section 4.2: When a step fails with a transient error (e.g. 429/timeout),
    it is retried with backoff and succeeds on subsequent attempt.
    """
    ws_id = setup_tenancy["workspace_id"]
    job_id = str(uuid.uuid4())
    job = RenderJob(id=job_id, workspace_id=ws_id, title="Retry Reel", status="processing")
    db.add(job)
    db.commit()

    attempts = {"count": 0}
    def flaky_executor(provider: str, params: dict):
        attempts["count"] += 1
        if attempts["count"] < 2:
            raise StepExecutionError("HTTP 429 Rate limit exceeded", error_class=ErrorClass.TRANSIENT)
        return {"status": "ok", "image_url": "/storage/images/scene_flaky.jpg"}

    result = StepLedgerOrchestrator.execute_step(
        db=db,
        job_id=job_id,
        workspace_id=ws_id,
        step_key="image",
        scene_index=5,
        params={"prompt": "scene 5 dramatic sunset"},
        step_executor=flaky_executor,
        max_retries=3
    )
    assert result["status"] == "ok"
    assert attempts["count"] == 2

    # Verify step ledger record
    step = db.query(JobStep).filter(JobStep.job_id == job_id, JobStep.scene_index == 5).first()
    assert step.status == "SUCCEEDED"
    assert step.attempt == 2
    assert step.error_class is None

def test_circuit_breaker_and_provider_fallback(setup_tenancy, db: Session):
    """
    Spec Section 4.2 & 4.4: Repeated provider failures open circuit breaker,
    routing traffic to fallback provider in chain.
    """
    breaker = CircuitBreaker(failure_threshold=2, cooldown_seconds=10.0)
    assert breaker.state == CircuitState.CLOSED
    assert breaker.allow_request() is True

    # 1. Fail twice
    breaker.record_failure()
    assert breaker.state == CircuitState.CLOSED
    breaker.record_failure()
    assert breaker.state == CircuitState.OPEN
    assert breaker.allow_request() is False

    # 2. Test ProviderRouter skips failing provider
    CircuitBreakerRegistry.reset_all()
    primary_breaker = CircuitBreakerRegistry.get_breaker("flux_schnell")
    primary_breaker.record_failure()
    primary_breaker.record_failure()
    primary_breaker.record_failure()
    assert primary_breaker.state == CircuitState.OPEN

    candidates = ProviderRouter.get_candidate_providers("image", plan_tier="free")
    candidate_ids = [c["id"] for c in candidates]
    assert "flux_schnell" not in candidate_ids, "Failing provider with open circuit must be skipped!"
    assert "pollock_stock" in candidate_ids or "solid_color_degrade" in candidate_ids

def test_degradation_policy_on_image_exhaustion(setup_tenancy, db: Session):
    """
    Spec Section 4.2: If all image providers fail, apply graceful degradation
    (fallback asset) and mark job as succeeded_degraded.
    """
    ws_id = setup_tenancy["workspace_id"]
    job_id = str(uuid.uuid4())
    job = RenderJob(id=job_id, workspace_id=ws_id, title="Degraded Reel", status="processing")
    db.add(job)
    db.commit()

    def always_fail(provider: str, params: dict):
        raise StepExecutionError("Provider 500 downstream outage", error_class=ErrorClass.PROVIDER_DOWN)

    res = StepLedgerOrchestrator.execute_step(
        db=db,
        job_id=job_id,
        workspace_id=ws_id,
        step_key="image",
        scene_index=3,
        params={"prompt": "unrenderable complex scene"},
        step_executor=always_fail,
        max_retries=1
    )
    assert res["degraded"] is True
    assert "fallback" in res["image_url"]

    step = db.query(JobStep).filter(JobStep.job_id == job_id, JobStep.scene_index == 3).first()
    assert step.status == "DEGRADED"

    db.refresh(job)
    assert job.degraded is True
    assert job.status == "succeeded_degraded"

def test_platform_fatal_error_refunds_quota(setup_tenancy, db: Session):
    """
    Spec Section 4.2 / 15.10: Unrecoverable platform failure refunds tenant's consumed quota.
    """
    ws_id = setup_tenancy["workspace_id"]
    period = datetime.now(timezone.utc).strftime("%Y-%m")

    # Increment quota to 1
    EntitlementService.consume_video_quota(db, ws_id)
    counter_before = db.query(UsageCounter).filter(
        UsageCounter.workspace_id == ws_id,
        UsageCounter.period == period,
        UsageCounter.metric == "videos_rendered"
    ).first()
    initial_count = counter_before.count

    job_id = str(uuid.uuid4())
    job = RenderJob(id=job_id, workspace_id=ws_id, title="Fatal Crash Reel", status="processing")
    db.add(job)
    db.commit()

    def fatal_step(provider: str, params: dict):
        raise StepExecutionError("Fatal unrecoverable OS kernel memory error", error_class=ErrorClass.FATAL)

    with pytest.raises(StepExecutionError):
        StepLedgerOrchestrator.execute_step(
            db=db,
            job_id=job_id,
            workspace_id=ws_id,
            step_key="compose",
            scene_index=None,
            params={"video": "broken.raw"},
            step_executor=fatal_step,
            max_retries=1
        )

    # Verify quota counter was automatically refunded
    db.refresh(counter_before)
    assert counter_before.count == initial_count - 1, "Fatal platform error must refund consumed video quota!"

def test_orchestrator_reaper_stale_heartbeat_recovery(setup_tenancy, db: Session):
    """
    Spec Section 4.4: Worker crash safety: reaper marks steps RUNNING with no heartbeat as PENDING.
    """
    ws_id = setup_tenancy["workspace_id"]
    job_id = str(uuid.uuid4())
    job = RenderJob(id=job_id, workspace_id=ws_id, title="Crashed Worker Reel", status="processing")
    db.add(job)

    stale_time = datetime.now(timezone.utc) - timedelta(seconds=300)
    stale_step = JobStep(
        job_id=job_id,
        workspace_id=ws_id,
        step_key="image",
        scene_index=1,
        status="RUNNING",
        input_hash="hash_reaper_test_01",
        heartbeat_at=stale_time
    )
    db.add(stale_step)
    db.commit()

    reaped = OrchestratorReaper.reap_stale_steps(db, timeout_seconds=60)
    assert len(reaped) >= 1
    assert any(r["job_id"] == job_id for r in reaped)

    db.refresh(stale_step)
    assert stale_step.status == "PENDING"
    assert "heartbeat timeout" in stale_step.error_detail

def test_weighted_fair_queue_guaranteed_free_share_cap_02():
    """
    CAP-02: Under heavy paid-plan load, Free plan retains guaranteed min 20% capacity share.
    """
    sim = FairQueueAdmissionController.simulate_weighted_fair_queue_share(
        free_jobs_count=50,
        paid_jobs_count=200,
        total_slots=100
    )
    assert sim["guaranteed_floor_satisfied"] is True
    assert sim["free_share_percent"] >= 20.0
    assert sim["free_slots_allocated"] >= 20

def test_admission_control_daily_cap_protection_cap_01(setup_tenancy, db: Session):
    """
    CAP-01: When global daily cap is reached, jobs are accepted as QUEUED_DEFERRED
    with an honest computed ETA instead of being dropped.
    """
    # Temporarily set system daily cap to 0
    setting = db.query(SystemSetting).filter(SystemSetting.key == "max_videos_per_day").first()
    original_val = setting.value if setting else {"cap": 100}

    if not setting:
        setting = SystemSetting(key="max_videos_per_day", value={"cap": 0})
        db.add(setting)
    else:
        setting.value = {"cap": 0}
    db.commit()

    try:
        admission = FairQueueAdmissionController.check_admission_control(db, plan_tier="free")
        assert admission["admitted"] is False
        assert admission["status"] == "QUEUED_DEFERRED"
        assert "GLOBAL_DAILY_CAP_REACHED" in admission["reason"]
        assert admission["estimated_eta_seconds"] >= 3600
        assert "Tomorrow 00:00 UTC" in admission["honest_eta_human"]
    finally:
        # Reset back
        setting.value = original_val
        db.commit()

def test_full_pipeline_dag_submission_and_ledger_api(setup_tenancy, db: Session):
    """
    End-to-End API Test:
    Submit job via POST /api/v1/jobs/submit, query GET /api/v1/jobs/{id}/ledger.
    Verify script, fan-out images, TTS, and compose steps are tracked in the ledger.
    """
    ws_id = setup_tenancy["workspace_id"]
    submit_res = client.post(
        "/api/v1/jobs/submit",
        json={
            "workspace_id": ws_id,
            "topic": "The mystery of deep sea creatures",
            "niche": "emotional_drama",
            "language": "Tamil",
            "voice": "ta-IN-ValluvarNeural"
        }
    )
    assert submit_res.status_code == 202, submit_res.text
    data = submit_res.json()
    assert "job_id" in data
    assert data["status"] in ["completed", "succeeded_degraded", "queued_deferred"]
    job_id = data["job_id"]

    # Inspect Step Ledger
    ledger_res = client.get(f"/api/v1/jobs/{job_id}/ledger")
    assert ledger_res.status_code == 200
    ledger = ledger_res.json()
    assert ledger["job_id"] == job_id
    assert "steps" in ledger
    assert len(ledger["steps"]) >= 4

    step_keys = [s["step_key"] for s in ledger["steps"]]
    assert "script" in step_keys
    assert "image" in step_keys
    assert "tts" in step_keys
    assert "compose" in step_keys
