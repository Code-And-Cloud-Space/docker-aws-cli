# Project Discussions & Architectural Decision Records (ADRs)

This document captures discussion notes, design requirements, and Architectural Decision Records (ADRs) for the Salesforce-AWS integration project.

---

## 🏛️ Architectural Decision Records (ADRs)

### ADR-001: Local Development First with Docker & LocalStack
- **Date:** 2026-09-05
- **Status:** Accepted
- **Decision:** Replicate AWS cloud architecture inside Docker using **LocalStack Community** (S3, DynamoDB, SQS, SNS, Secrets Manager), with a local web dashboard on port `3000`.

---

### ADR-002: Event-Driven Asynchronous Integration via SQS & Event Engine
- **Date:** 2026-09-05
- **Status:** Accepted
- **Decision:** Salesforce updates are asynchronously mirrored into DynamoDB and S3 via SQS queues with Dead Letter Queues (DLQ).

---

### ADR-003: Unified Antigravity & AI Agent Instruction Architecture
- **Date:** 2026-09-05
- **Status:** Accepted
- **Decision:** Standardize pair-programming guidelines and file linking rules across AI agents.

---

### ADR-004: Direct Live Salesforce Org Connectivity from Docker
- **Date:** 2026-09-05
- **Status:** Accepted
- **Decision:** Connect directly to Live Salesforce Orgs (Developer Org, Sandbox, or Production) from within the Docker environment.

---

### ADR-005: Mandatory AI Safeguard for Continuous Documentation
- **Date:** 2026-09-05
- **Status:** Accepted
- **Decision:** Enforce continuous updates to the `docs/` folder on every AI turn via always-on Antigravity rule [`.agents/rules/mandatory-documentation-safeguard.md`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/.agents/rules/mandatory-documentation-safeguard.md).

---

### ADR-006: Monorepo `src/` Module Hierarchy & Vercel CLI Development Server
- **Date:** 2026-09-05
- **Status:** Accepted
- **Decision:** Consolidate all application development code under `src/` and use Vercel's serve engine on port 3000.

---

### ADR-007: OAuth 2.0 Authorization Code Flow, Replicated Secrets Manager & MySQL Multi-User Token Expiry Engine
- **Date:** 2026-09-05
- **Status:** Accepted
- **Decision:** Implement Salesforce OAuth 2.0 Auth Code flow with Callback URL, AWS Secrets Manager for Refresh Tokens, and MySQL table for token expiration management.

---

### ADR-008: Host Port Mapping Isolation for MySQL (`3307:3306`)
- **Date:** 2026-09-05
- **Status:** Accepted
- **Decision:** Map container MySQL port `3306` to host port `3307` (`${MYSQL_HOST_PORT:-3307}:3306`), isolating it from local host port collisions.

---

### ADR-009: LocalStack Community Image Pinning (`localstack/localstack:3.8`)
- **Date:** 2026-09-05
- **Status:** Accepted
- **Decision:** Pin LocalStack image to stable community release `localstack/localstack:3.8` with `ACTIVATE_PRO=0` to ensure zero-license, free local development for S3, DynamoDB, SQS, SNS, and Secrets Manager.

---

### ADR-010: Scopes Sanitization (Removed `id` Scope)
- **Date:** 2026-09-05
- **Status:** Accepted
- **Decision:** Configured OAuth authorization request with `scope=api refresh_token offline_access`.

---

### ADR-011: Proof Key for Code Exchange (PKCE / RFC 7636) Extension
- **Date:** 2026-09-05
- **Status:** Accepted
- **Decision:** Implement RFC 7636 PKCE for Salesforce OAuth 2.0.

---

### ADR-012: MySQL Relational Schema for Salesforce CRM Objects (Account, Contact, Opportunity)
- **Date:** 2026-09-05
- **Status:** Accepted
- **Decision:** Implement dedicated relational tables in MySQL (`salesforce_accounts`, `salesforce_contacts`, `salesforce_opportunities`).

---

### ADR-013: Direct Salesforce Login Model & Multi-Target Single Record Sync
- **Date:** 2026-09-05
- **Status:** Accepted
- **Decision:** Removed static `users` table and bound authentication directly to Live Salesforce OAuth.

---

### ADR-014: Strict Browser Session Isolation & Disconnected Access Blocking
- **Date:** 2026-09-05
- **Status:** Accepted
- **Decision:**
  1. Isolate user logins on a per-browser / incognito window basis using `sessionStorage` and `X-Session-ID`.
  2. In `get_valid_token`, strictly reject requests without a valid `session_id` and return HTTP 401 Unauthorized.
  3. Ensure no data is loaded in the Salesforce Explorer when a window or tab is in a disconnected state.
  4. Ensure MySQL Synced DB and AWS Explorers handle session boundaries consistently.

---

### ADR-015: Universal Zero-Trust Disconnected Data Guard Across Entire Platform
- **Date:** 2026-09-06
- **Status:** Accepted
- **Context:** User required that if no Salesforce connection is active, NO data whatsoever should be visible or queryable anywhere (including MySQL DB, DynamoDB, S3 files, SQS queues, Secrets Manager, and integration audit logs).
- **Decision:**
  1. Implemented a universal FastAPI dependency `require_authenticated_salesforce_session` in [`src/integration-engine/app/main.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/main.py) protecting ALL data inspection endpoints (`/api/db/*`, `/api/aws/*`, `/api/secrets`, `/api/logs`, `/api/sync/*`, `/api/salesforce/*`).
  2. Any request missing an active authenticated Salesforce session immediately receives `401 Unauthorized`.
  3. In [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js), established `renderLockedStateForAllTabs()` and global `isSalesforceConnected` state tracking, instantly zeroing and locking every dashboard tab (Salesforce Live, MySQL DB, AWS DynamoDB, AWS S3, AWS SQS, Secrets Manager, and Audit Logs) whenever Salesforce is disconnected.
  4. Set initial HTML placeholders in [`src/dashboard-ui/index.html`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/index.html) to render locked banners by default before any network roundtrip.

---

### ADR-016: Live Volume Mounting & Instant Hot-Reloading for Local Development
- **Date:** 2026-09-06
- **Status:** Accepted
- **Context:** User requested direct reflection of local code edits in Docker without manual container rebuilds.
- **Decision:**
  1. Mounted host directory `./src/integration-engine/app` to `/app/app` inside `integration-sync-engine` and added `--reload` to Uvicorn in [`docker-compose.yml`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docker-compose.yml).
  2. Mounted host directory `./src/dashboard-ui` to `/app` inside `integration-dashboard-ui` in [`docker-compose.yml`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docker-compose.yml).
  3. Edits to backend Python services auto-reload via WatchFiles; edits to UI files (`index.html`, `app.js`) reflect instantly on browser refresh.

---

### ADR-017: Non-Blocking Glassmorphic Toast Notification Engine
- **Date:** 2026-09-06
- **Status:** Accepted
- **Context:** Synchronous browser `alert()` dialogs interrupt user workflows, block event loops, and look dated.
- **Decision:**
  1. Replace all native browser `alert()` dialogs with a modern, glassmorphic toast notification engine.
  2. Add fixed top-right `#toast-container` in [`src/dashboard-ui/index.html`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/index.html) supporting dynamic toast stacking.
  3. Support four semantic categories (`success`, `error`, `warning`, `info`) with contextual icons, auto-dismiss timers, manual dismiss buttons, and CSS cubic-bezier slide transitions.
  4. Override `window.alert` to route to `showToast` to catch any accidental unhandled alerts.

---

## 💬 Discussion Notes Log

### Session 1-18: Foundational Architecture & Multi-Target Sync
- Implemented OAuth 2.0 PKCE, MySQL relational CRM tables, LocalStack, and single-record sync.

### Session 19: Session Isolation Consistency & Data Leakage Prevention
- Enforced strict `session_id` requirement in `get_valid_token`.
- Added HTTP 401 status checks on all Salesforce endpoints in [`src/integration-engine/app/main.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/main.py).
- Added connection guards in [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js) to display a clear locked state message instead of attempting API calls when disconnected.

### Session 20: Complete Platform URL & Endpoint Catalog
- Documented all web interfaces, interactive API documentation (Swagger UI, ReDoc, OpenAPI schema), and backend endpoints in [`docs/setup-guide.md`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docs/setup-guide.md).

### Session 21: Complete Lockout of All Data When Disconnected
- Applied `require_authenticated_salesforce_session` dependency across MySQL DB, AWS DynamoDB, S3 files, SQS stats, Secrets Manager, and Audit Logs.
- Re-built and verified backend and frontend containers. Tested that all unauthenticated queries return `401 Unauthorized`.
- Hid the **Sync Pipelines** tab (`#tab-btn-sync`) whenever Salesforce is not connected or logged out, preventing unauthenticated access to sync triggers.

### Session 22: Live Code Volume Mounting & Instant Hot-Reloading
- Configured bind-mount volumes for backend (`./src/integration-engine/app:/app/app`) and frontend (`./src/dashboard-ui:/app`).
- Enabled Uvicorn `--reload` watcher inside Docker for instantaneous zero-rebuild local development.

### Session 23: MySQL Column Migration for `session_id`
- Altered `salesforce_oauth_tokens` table in MySQL to add missing `session_id` column and index.
- Added programmatic migration handler inside `init_db()` in [`src/integration-engine/app/database.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/database.py).
- Synchronized [`src/scripts/init-mysql.sql`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/scripts/init-mysql.sql).

### Session 24: Legacy `user_id` Foreign Key & Column Removal in `salesforce_oauth_tokens`
- Diagnosed MySQL Error 1364 (`Field 'user_id' doesn't have a default value`) during OAuth callback.
- Dropped legacy constraint `salesforce_oauth_tokens_ibfk_1`, composite index `idx_user_active`, and column `user_id` from the MySQL database.
- Added programmatic migration handler inside `init_db()` in [`src/integration-engine/app/database.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/database.py) to guarantee schema compatibility across all environments.

### Session 25: Replaced Native `alert()` with Toast Notification Engine
- User requested replacing intrusive browser `alert()` popups with a toast notification system.
- Implemented `showToast()` and `dismissToast()` in [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js) with semantic styling (`success`, `error`, `warning`, `info`) and CSS slide-in animations in [`src/dashboard-ui/index.html`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/index.html).
- Replaced all 24 `alert()` occurrences across the dashboard application.

### Session 26: First-Time Screen Load Connection Check & Auto-Hydration
- User requested checking connection status immediately when the screen loads for the first time.
- Made `refreshAll()` an `async` function that awaits `checkHealth()` on `DOMContentLoaded`.
- Ensures accurate validation of the Salesforce session state against `GET /api/status` before rendering locked or hydrated views, automatically populating CRM and AWS records on initial load if connected.


