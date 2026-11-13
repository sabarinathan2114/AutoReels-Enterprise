# AutoReels Enterprise v2.0 — Production Operations Runbook

**Document Version:** 2.0.0  
**Classification:** Enterprise Operations & Disaster Recovery  
**Governing Standard:** Master Build Specification v2.0 & Section 15 Free-First Addendum  

---

## 1. System Architecture & Prerequisites

### 1.1 Infrastructure Stack
- **Database:** MySQL 8.0+ / MariaDB on port `3306` (Database: `autoreels_db`).
- **Backend Server:** Python 3.12+ FastAPI running on port `8000`.
- **Frontend Studio:** Next.js 16 (App Router) running on port `3000`.
- **Media Engine:** Subprocess FFmpeg binary via `imageio-ffmpeg` with `libx264`, `aac`, and `ass` filters.
- **Storage:** Local file store (`backend/storage/`) partitioned into `audio/`, `images/`, `video/`, `output/`.

---

## 2. Cold Boot & Service Startup

### 2.1 One-Click Launch (Windows)
Execute the unified root script:
```bat
run_app.bat
```

### 2.2 Manual Step-by-Step Launch
1. **Ensure MySQL Service is Running:**
   ```bash
   # Windows Services
   net start MySQL80
   ```
2. **Apply Database Migrations & Seed Baseline:**
   ```bash
   cd backend
   alembic upgrade head
   python -m app.cli.admin_cli create-admin --email admin@autoreels.local --password "MasterAdmin2026!" --role SUPERADMIN
   ```
3. **Start FastAPI Backend (Port 8000):**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
4. **Start Next.js Frontend (Port 3000):**
   ```bash
   cd ../frontend
   npm run build
   npm run start
   ```

---

## 3. Health Checks & Synthetic Monitoring

AutoReels Enterprise exposes dedicated liveness and readiness probes:

| Probe | Endpoint | Expected Status | Diagnostic Action on Failure |
| :--- | :--- | :--- | :--- |
| **Liveness** | `GET /health/live` | `{"status": "alive"}` (HTTP 200) | Pod/process restart required. |
| **Readiness** | `GET /health/ready` | `{"database": "connected"}` (HTTP 200) | Verify MySQL connection pool and network port 3306. |
| **Plans Matrix** | `GET /api/plans` | List of 4 plans (Free, A, B, C) | Re-seed plans table: `python -m app.cli.admin_cli seed-plans`. |

---

## 4. Emergency Incident Response: Compromised Token Revocation (SEC-22)

When an API token, user account, or creator credential is reported leaked:

### 4.1 Revoking via Public API
```bash
curl -X POST https://api.autoreels.com/api/v1/auth/revoke \
  -H "Authorization: Bearer <COMPROMISED_JWT>" \
  -H "Content-Type: application/json" \
  -d '{"reason": "emergency_credential_leak"}'
```

### 4.2 Revoking via MySQL Directly
If the server is unreachable via HTTP:
```sql
USE autoreels_db;

-- Hash token with SHA-256 and insert into blacklist
INSERT INTO revoked_tokens (id, token_hash, user_id, revoked_at, reason)
VALUES (
  UUID(),
  SHA2('<COMPROMISED_TOKEN_STRING>', 256),
  <USER_ID>,
  NOW(),
  'security_incident_revocation'
);
```
All subsequent API requests bearing that token will receive HTTP 401 `TOKEN_REVOKED`.

---

## 5. Quota & Admission Control Management

### 5.1 Increasing Global Daily Render Cap
When viral demand spikes or during launch promotions, the Super Admin can expand the daily render cap without restarting the servers:
```bash
curl -X POST https://api.autoreels.com/api/v1/admin/settings \
  -H "Authorization: Bearer <SUPERADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"daily_render_cap": 2500}'
```

### 5.2 Refunding Creator Quota After Outage
If a platform crash or provider network error interrupts a creator's render, the pipeline orchestrator automatically refunds quota (`PIPE-005`). To manually refund an affected workspace:
```sql
UPDATE usage_counters
SET count = GREATEST(0, count - 1), updated_at = NOW()
WHERE workspace_id = '<WORKSPACE_ID>'
  AND period = DATE_FORMAT(NOW(), '%Y-%m')
  AND metric = 'videos_rendered';
```

---

## 6. Disaster Recovery & Database Rollback

### 6.1 Daily Automated Backup Procedure
```bash
mysqldump -u root -p autoreels_db --single-transaction --quick > /backups/autoreels_$(date +%F_%H%M).sql
```

### 6.2 Restoration from Snapshot
```bash
mysql -u root -p -e "DROP DATABASE IF EXISTS autoreels_db; CREATE DATABASE autoreels_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p autoreels_db < /backups/autoreels_snapshot.sql
cd backend && alembic upgrade head
```

---

## 7. Security Hardening Policies

- **Rate Limits:** Sensitive auth routes capped at 5 req/min (`SEC-11`); general routes capped at 60 req/min (`SEC-12`).
- **HTTP Headers:** Injected on every response (`SEC-19`): `nosniff`, `DENY` frames, `max-age=31536000` HSTS, strict CSP.
- **Upload Guards:** Enforces magic bytes inspection on PNG (`\x89PNG`), JPEG (`\xff\xd8\xff`), MP3 (`ID3`), MP4 (`ftyp`) and scrubs path traversal (`SEC-14`).
- **SSRF Shields:** Trend Radar blocks loopback (`127.0.0.1`), RFC1918 private subnets, and cloud metadata (`169.254.169.254`) (`SEC-13`).
