from app.config.settings import Settings

def test_default_settings():
    """Verify default enterprise configuration matches Spec v2.0."""
    settings = Settings()
    assert settings.APP_NAME == "AutoReels Enterprise"
    assert settings.APP_VERSION == "2.0.0"
    assert settings.SPEC_VERSION == "2.0 (Free-First Addendum)"
    assert settings.DEFAULT_PLAN == "FREE"
    assert settings.DEFAULT_MONTHLY_QUOTA == 2
    assert settings.DEFAULT_RESOLUTION == "720x1280"
    assert settings.WATERMARK_ENABLED_DEFAULT is True
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 15
    assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 30

def test_database_url_configuration():
    """Ensure database connection string is properly structured."""
    settings = Settings()
    assert "mysql" in settings.DATABASE_URL or "sqlite" in settings.DATABASE_URL
