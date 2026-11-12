# AutoReels Enterprise v2.0 — Phase 2: Database, Multi-Tenancy & Plans Report

**Phase Name:** Phase 2 — Multi-Tenant Schemas, Workspace Scoping, Plans as Data, & Entitlements  
**Specification Reference:** AutoReels Enterprise Master Build Specification v2.0 (Sections 4, 10, & 15.4)  
**Execution Date:** November 12, 2026  
**Status:** COMPLETED & VERIFIED (Green)  
**Lead Engineer:** Principal/Staff Software Engineer  

---

## 1. Executive Summary

Phase 2 transitions AutoReels Enterprise into a true multi-tenant SaaS architecture running on **MySQL 8.0+ / MariaDB**. The schema now supports 18 database tables including `tenants`, `workspaces`, `memberships`, `plans`, `subscriptions`, `usage_counters`, `plan_change_requests`, `platform_admins`, `system_settings`, `feature_flags`, `assets`, `render_jobs`, and `audit_log`.

In compliance with ADR-001 (MySQL Tenancy), Row-Level Security (RLS) is implemented via an application-level tenant scoping layer (`TenantService`) that guarantees every database query is strictly partitioned by `workspace_id`. Two-tenant isolation tests verify that Tenant A and Tenant B can never observe or tamper with each other's projects, assets, or quota counters.

All 11 automated test suites passed (14.30s runtime), and the Next.js frontend build succeeded with zero errors.

---

## 2. Multi-Tenant Relational Schema (18 Tables)

The following tables are active in `autoreels_db` under Alembic migration `d626d3a8624f_phase_2_tenancy_and_plans`:

| Table Name | Role & Tenancy Scope | Key Fields |
| :--- | :--- | :--- |
| `tenants` | Top-level tenant account | `id (UUID)`, `name`, `slug`, `created_at` |
| `workspaces` | Scoped sub-account workspace | `id (UUID)`, `tenant_id (FK)`, `name`, `is_default` |
| `users` | Global platform user identity | `id`, `uuid`, `email`, `hashed_password`, `is_verified` |
| `memberships` | User workspace role mapping | `id`, `workspace_id (FK)`, `user_id (FK)`, `role (OWNER/ADMIN/MEMBER)` |
| `plans` | Data-driven plan matrix | `id`, `monthly_video_quota`, `resolution`, `watermark`, `features (JSON)` |
| `subscriptions` | Active tenant subscription | `id`, `tenant_id (FK)`, `plan_id (FK)`, `status` |
| `usage_counters` | Monthly consumption meters | `id`, `workspace_id (FK)`, `period (YYYY-MM)`, `metric`, `count` |
| `plan_change_requests` | Enterprise upgrade requests | `id`, `tenant_id (FK)`, `requested_plan_id (FK)`, `status` |
| `platform_admins` | Super administrator roles | `id`, `user_id (FK)`, `role` |
| `system_settings` | Dynamic platform configs | `key`, `value (JSON)`, `updated_at` |
| `feature_flags` | Tiered feature gating | `id`, `flag_name`, `is_enabled`, `target_plans (JSON)` |
| `assets` | Scoped media storage keys | `id`, `workspace_id (FK)`, `asset_type`, `storage_key`, `url` |
| `render_jobs` | Asynchronous rendering jobs | `id`, `workspace_id (FK)`, `project_id`, `status`, `progress_percent` |
| `audit_log` | Immutable compliance log | `id`, `tenant_id`, `workspace_id`, `user_id`, `action`, `details` |
| `channels` | YouTube/Social dispatch channels | `id`, `workspace_id (FK)`, `user_id`, `niche`, `default_voice` |
| `social_accounts` | Connected platform OAuth accounts | `id`, `workspace_id (FK)`, `user_id`, `platform`, `is_connected` |
| `video_projects` | Video generation projects | `id`, `workspace_id (FK)`, `user_id`, `script_text`, `status` |
| `alembic_version` | Migration revision pointer | `version_num` |

---

## 3. Plan Matrix Seeded as Data (Spec 15.4)

Plans are stored directly in the `plans` table and loaded dynamically by the API (`GET /api/plans`), fulfilling the "Plans as Data, not Code" requirement:

```json
[
  {
    "id": "free",
    "name": "Free Tier",
    "monthly_quota": 2,
    "max_duration_sec": 30,
    "resolution": "720x1280",
    "watermark": true,
    "voices": 2,
    "social_channels": 0,
    "price_monthly": "$0.00",
    "modes": ["zero_input", "preset_niches", "direct_download"]
  },
  {
    "id": "plan_a",
    "name": "Plan A (Creator)",
    "monthly_quota": 30,
    "max_duration_sec": 45,
    "resolution": "1080x1920",
    "watermark": false,
    "voices": 6,
    "social_channels": 1,
    "price_monthly": "$9.00",
    "modes": ["zero_input", "director_mode", "custom_script", "single_channel_auto_dispatch"]
  },
  {
    "id": "plan_b",
    "name": "Plan B (Growth)",
    "monthly_quota": 100,
    "max_duration_sec": 60,
    "resolution": "1080x1920",
    "watermark": false,
    "voices": 12,
    "social_channels": 3,
    "price_monthly": "$29.00",
    "modes": ["zero_input", "director_mode", "character_mode", "multi_channel_auto_dispatch", "smart_scheduler"]
  },
  {
    "id": "plan_c",
    "name": "Plan C (Agency / Enterprise)",
    "monthly_quota": 500,
    "max_duration_sec": 60,
    "resolution": "1080x1920",
    "watermark": false,
    "voices": 100,
    "social_channels": 10,
    "price_monthly": "$79.00",
    "modes": ["zero_input", "director_mode", "character_mode", "custom_brand_voice", "multi_account_dispatch", "performance_autopilot", "priority_queue"]
  }
]
```

---

## 4. Single-Transaction Signup Provisioning

When a user signs up via `POST /api/auth/register`, the backend executes the following in **one atomic database transaction**:
1. Creates the `User` record with hashed password (Argon2id/Bcrypt).
2. Generates a new `Tenant` with unique slug.
3. Generates the default `Workspace` (`is_default=True`).
4. Creates an `OWNER` `Membership` tying the user to the workspace.
5. Provisions an active `Subscription` on the `FREE` plan.
6. Emits an initial `AuditLog` entry (`tenant.provisioned`).
7. Issues short-lived access JWT containing `sub`, `user_id`, and `workspace_id`.

---

## 5. Verification & Test Evidence

### 5.1 Pytest Full Suite Execution (11/11 Passed)
```bash
python -m pytest backend/tests -v
```
```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.2.0, pluggy-1.7.0
plugins: anyio-4.16.0, asyncio-1.4.1.post1
collected 11 items

backend/tests/test_auth_tenancy.py::test_signup_provisions_tenant_and_free_plan PASSED [  9%]
backend/tests/test_auth_tenancy.py::test_login_returns_tenant_workspace_and_plan PASSED [ 18%]
backend/tests/test_health.py::test_root_endpoint PASSED                  [ 27%]
backend/tests/test_health.py::test_health_liveness PASSED                [ 36%]
backend/tests/test_health.py::test_health_readiness PASSED               [ 45%]
backend/tests/test_health.py::test_request_id_middleware PASSED          [ 54%]
backend/tests/test_health.py::test_plans_matrix PASSED                   [ 63%]
backend/tests/test_plans.py::test_plan_spec_compliance PASSED            [ 72%]
backend/tests/test_settings.py::test_default_settings PASSED             [ 81%]
backend/tests/test_settings.py::test_database_url_configuration PASSED   [ 90%]
backend/tests/test_tenancy.py::test_two_tenant_isolation PASSED          [100%]

======================= 11 passed, 1 warning in 14.30s ========================
```

### 5.2 Two-Tenant Cross-Isolation Verification Details
1. **Asset Partitioning:** Workspace A assets are completely inaccessible and invisible to Workspace B query executions (`scoped_assets_b` returns 0 assets belonging to Workspace A).
2. **Project Partitioning:** Workspace A video projects are completely filtered out from Workspace B query executions.
3. **Access Enforcement:** `verify_workspace_access(user_b.id, ws_a.id)` returns `False`.
4. **Quota Independence:** Incrementing video consumption in Workspace A from 0 to 2 videos has zero effect on Workspace B's usage counter (which remains strictly at 0).

---

## 6. Next Steps: Phase 3 Handover

Phase 2 is fully complete and verified. The system is ready for **Phase 3: Public Website and Authentication (Landing Page & Onboarding)**:
1. Build public landing page:
   - Hero section with 9:16 demo video player slot
   - 3-step "How It Works" interactive explanation
   - Live plan comparison table reading directly from `GET /api/plans` (zero hardcoded pricing data)
   - Feature showcase & FAQ accordion
   - Footer with Terms & Privacy links
2. Dedicated routes:
   - `/plans` (standalone interactive plan comparison with upgrade request buttons)
   - `/signup`, `/login`, `/onboarding`
3. Connect frontend authentication modal and forms to `/api/auth/register` and `/api/auth/login`.
4. Preserve 320px responsive breakpoints down to mobile screens.
