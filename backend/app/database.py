import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.settings import settings

logger = logging.getLogger("autoreels.database")

# Build engine arguments
engine_kwargs = {
    "pool_pre_ping": settings.DB_POOL_PRE_PING,
    "pool_recycle": settings.DB_POOL_RECYCLE_SEC,
}

if "sqlite" in settings.DATABASE_URL:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_size"] = settings.DB_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW

try:
    engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
    # Test connection immediately
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.info(f"Database connected successfully to {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'local'}")
except Exception as e:
    logger.warning(f"Primary database connection failed ({e}). Falling back to SQLite local database.")
    FALLBACK_URL = "sqlite:///./autoreels_dev.db"
    engine = create_engine(FALLBACK_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_connection() -> bool:
    """Readiness probe helper to check DB health."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as ex:
        logger.error(f"Database health check failed: {ex}")
        return False
