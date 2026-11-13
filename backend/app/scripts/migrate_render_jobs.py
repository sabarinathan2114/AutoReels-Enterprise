from sqlalchemy import text
from app.database import engine

def migrate():
    cols = [
        ("title", "VARCHAR(255) DEFAULT 'Untitled Reel'"),
        ("current_step", "VARCHAR(50) NULL"),
        ("degraded", "TINYINT(1) DEFAULT 0"),
        ("plan_tier", "VARCHAR(50) DEFAULT 'free'"),
        ("estimated_duration_sec", "INT DEFAULT 90"),
        ("heartbeat_at", "DATETIME NULL"),
        ("output_video_path", "VARCHAR(500) NULL")
    ]
    with engine.connect() as conn:
        for col_name, col_def in cols:
            try:
                conn.execute(text(f"ALTER TABLE render_jobs ADD COLUMN {col_name} {col_def}"))
                conn.commit()
                print(f"[DB] Added column {col_name} to render_jobs")
            except Exception as e:
                print(f"[DB] Column {col_name} already exists or error: {e}")

if __name__ == "__main__":
    migrate()
