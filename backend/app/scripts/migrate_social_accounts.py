"""
Adds social channel health, privacy, and resumable session columns to social_accounts table.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.database import engine
from sqlalchemy import text

def migrate_social_accounts():
    with engine.connect() as conn:
        cols = conn.execute(text("SHOW COLUMNS FROM social_accounts")).fetchall()
        existing = [c[0] for c in cols]
        
        alter_stmts = []
        if "health_status" not in existing:
            alter_stmts.append("ADD COLUMN health_status VARCHAR(50) DEFAULT 'CONNECTED'")
        if "privacy_status" not in existing:
            alter_stmts.append("ADD COLUMN privacy_status VARCHAR(50) DEFAULT 'private'")
        if "resumable_session_uri" not in existing:
            alter_stmts.append("ADD COLUMN resumable_session_uri TEXT NULL")
        if "daily_published_count" not in existing:
            alter_stmts.append("ADD COLUMN daily_published_count INT DEFAULT 0")
        if "last_published_at" not in existing:
            alter_stmts.append("ADD COLUMN last_published_at DATETIME NULL")

        if alter_stmts:
            stmt = f"ALTER TABLE social_accounts {', '.join(alter_stmts)}"
            print(f"Executing: {stmt}")
            conn.execute(text(stmt))
            conn.commit()
            print("Successfully migrated social_accounts table!")
        else:
            print("All social_accounts columns already present.")

if __name__ == "__main__":
    migrate_social_accounts()
