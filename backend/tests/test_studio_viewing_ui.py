"""
Phase 8 Studio & Viewing UI Tests (Spec 15.4, 15.10)
Tests:
- Server-Sent Events (SSE) job progress streaming
- Workspace jobs history endpoint
- Free tier quota block on 3rd video with clear message
"""
import uuid
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.entities import User, Workspace, RenderJob, UsageCounter
from app.services.auth_service import AuthService
from app.services.tenant_service import TenantService

client = TestClient(app)

@pytest.fixture
def studio_workspace():
    """Provisions a clean tenant and workspace hierarchy on the Free tier."""
    db = SessionLocal()
    unique_email = f"studio_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        email=unique_email,
        hashed_password=AuthService.hash_password("Pass123!"),
        full_name="Studio User",
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    tenant_data = TenantService.create_tenant_hierarchy(
        db=db,
        user_id=user.id,
        tenant_name="Studio Test Workspace",
        plan_id="free"
    )
    ws_id = tenant_data["workspace_id"]
    db.close()
    return ws_id

def test_workspace_jobs_history_endpoint(studio_workspace):
    """Verifies GET /api/v1/jobs/workspace/{workspace_id} returns reel history"""
    db = SessionLocal()
    try:
        for i in range(3):
            job = RenderJob(
                id=str(uuid.uuid4()),
                workspace_id=studio_workspace,
                title=f"Test Reel Episode {i+1}",
                status="completed",
                plan_tier="free",
                estimated_duration_sec=30,
                output_video_url=f"/storage/video/test_{i}.mp4",
                created_at=datetime.now(timezone.utc)
            )
            db.add(job)
        db.commit()

        res = client.get(f"/api/v1/jobs/workspace/{studio_workspace}")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 3
        assert any("Test Reel Episode" in d["title"] for d in data)
        assert data[0]["status"] == "completed"
    finally:
        db.close()

def test_job_sse_stream_endpoint(studio_workspace):
    """Verifies GET /api/v1/jobs/{job_id}/stream yields SSE events"""
    db = SessionLocal()
    job_id = str(uuid.uuid4())
    try:
        job = RenderJob(
            id=job_id,
            workspace_id=studio_workspace,
            title="Streaming Test Reel",
            status="completed",
            current_step="finished",
            progress_percent=100,
            plan_tier="free",
            estimated_duration_sec=30,
            output_video_url=f"/storage/video/test_stream_{job_id}.mp4",
            created_at=datetime.now(timezone.utc)
        )
        db.add(job)
        db.commit()

        # Connect to SSE stream
        with client.stream("GET", f"/api/v1/jobs/{job_id}/stream") as response:
            assert response.status_code == 200
            assert "text/event-stream" in response.headers["content-type"]
            lines = []
            for line in response.iter_lines():
                if line:
                    lines.append(line)
                if len(lines) >= 2:
                    break
            assert len(lines) > 0
            assert any("Streaming Test Reel" in l or "job_id" in l for l in lines)
    finally:
        db.close()

def test_third_video_in_month_blocked_with_clear_message(studio_workspace):
    """
    Spec Acceptance: Logged-in Free user creates 2 videos; 
    the 3rd video in a month is blocked with a clear message.
    """
    db = SessionLocal()
    try:
        # 1. Simulate 2 videos consumed (Max for Free plan is 2)
        current_period = datetime.now(timezone.utc).strftime("%Y-%m")
        counter = db.query(UsageCounter).filter(
            UsageCounter.workspace_id == studio_workspace,
            UsageCounter.metric == "videos_rendered",
            UsageCounter.period == current_period
        ).first()

        if counter:
            counter.count = 2
        else:
            counter = UsageCounter(
                id=str(uuid.uuid4()),
                workspace_id=studio_workspace,
                metric="videos_rendered",
                period=current_period,
                count=2
            )
            db.add(counter)
        db.commit()

        # 2. Attempt 3rd video job submission via API
        res = client.post("/api/v1/jobs/submit", json={
            "workspace_id": studio_workspace,
            "topic": "3rd Attempted Video Over Quota",
            "niche": "daily_facts",
            "language": "English",
            "voice": "en-US-ChristopherNeural"
        })

        # 3. Verify HTTP 429 Quota Exceeded with clear actionable message
        assert res.status_code == 429
        detail = res.json()["detail"]
        if isinstance(detail, dict):
            assert detail.get("error") == "MONTHLY_QUOTA_EXCEEDED"
            assert "monthly limit" in detail.get("message", "").lower()
        else:
            assert "quota" in str(detail).lower()
    finally:
        db.close()
