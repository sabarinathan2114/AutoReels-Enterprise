import pytest
from app.database import SessionLocal
from app.models.entities import Plan
from app.services.plan_service import PlanService

@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()

def test_plan_spec_compliance(db):
    """
    Verifies that all 4 plans in database comply exactly with Spec Section 15.4:
    - Free: 2 quota, 720x1280, watermark=True
    - Plan A: 30 quota, 1080x1920, watermark=False
    - Plan B: 100 quota, 1080x1920, watermark=False
    - Plan C: 500 quota, 1080x1920, watermark=False
    """
    PlanService.seed_plans(db)
    plans = PlanService.get_all_active_plans(db)
    plan_map = {p.id: p for p in plans}

    assert "free" in plan_map
    assert "plan_a" in plan_map
    assert "plan_b" in plan_map
    assert "plan_c" in plan_map

    # Free plan verification
    free = plan_map["free"]
    assert free.monthly_video_quota == 2
    assert free.watermark is True
    assert free.resolution == "720x1280"
    assert free.monthly_price_cents == 0

    # Plan A verification
    pa = plan_map["plan_a"]
    assert pa.monthly_video_quota == 30
    assert pa.watermark is False
    assert pa.resolution == "1080x1920"
    assert pa.monthly_price_cents == 900

    # Plan B verification
    pb = plan_map["plan_b"]
    assert pb.monthly_video_quota == 100
    assert pb.watermark is False
    assert "character_mode" in pb.features

    # Plan C verification
    pc = plan_map["plan_c"]
    assert pc.monthly_video_quota == 500
    assert pc.watermark is False
    assert "custom_brand_voice" in pc.features
