# AutoReels Enterprise v2.0 — Architecture Decision Records (ADRs)

## ADR-001: Adoption of MySQL 8.0+ / MariaDB over PostgreSQL
- **Status:** Accepted (Overriding Section 4 of Spec v2.0 per explicit user directive)
- **Context:** The original specification drafted PostgreSQL with row-level security (RLS). The user host environment has MySQL/MariaDB natively installed and operating on port 3306, and explicitly mandated MySQL.
- **Decision:** Use MySQL 8.0+ / MariaDB with InnoDB storage engine, `utf8mb4_unicode_ci`, JSON column support, and application/ORM-level tenant scoping (`workspace_id` filter predicates on all tenant queries).
- **Consequences:** Eliminates PostgreSQL setup friction on developer machine; requires strict ORM-level tenant filtering (`workspace_id`) and composite indexes.

## ADR-002: Plan Matrix as Data Rows
- **Status:** Accepted (Spec Section 15.4)
- **Context:** Plans must not be hardcoded in application logic.
- **Decision:** Seed `plans` table with Free (2 videos/mo, 720p, watermark), Plan A, Plan B, and Plan C. Entitlements evaluated at runtime in backend.
- **Consequences:** Plans can be altered dynamically by Super Admin without redeployment.

## ADR-003: Zero Cash Cost Free Pipeline Architecture
- **Status:** Accepted (Spec Section 15.1 & 15.2)
- **Context:** Zero-cost generation is a non-negotiable constraint.
- **Decision:** Visual hierarchy: 1. Pexels/Pixabay stock $\to$ 2. Typographic gradient cards $\to$ 3. Pollinations Flux AI $\to$ 4. GPU worker (Plan B/C). Voice synthesis via Piper / Edge-TTS. Subtitles via faster-whisper / Edge-TTS karaoke tags.
- **Consequences:** Guarantees zero recurring API costs for the primary free generation path.

## ADR-004: Ass/Libass Kinetic Captions with FFmpeg
- **Status:** Accepted (Spec Section 8 & 15.3)
- **Context:** Vertical short-form videos require dynamic, centered kinetic word-by-word animated subtitles.
- **Decision:** Use FFmpeg with `libass` burning styled `.ass` karaoke subtitle files, positioned with 18% bottom safe zone and 8% top safe zone.
- **Consequences:** Produces high-retention social captions natively on CPU in seconds.

## ADR-005: Pydantic Settings & Health Probes Architecture
- **Status:** Accepted (Phase 1 Foundation)
- **Context:** Phase 1 requires production-grade configuration and observability.
- **Decision:** Use Pydantic V2 `SettingsConfigDict` with `.env` fallback, UUIDv4 request ID middleware, structured JSON logs, `/health/live` (process check), and `/health/ready` (active MySQL `SELECT 1` and storage write check).
- **Consequences:** Ensures seamless container healthchecks and local developer ergonomics.
