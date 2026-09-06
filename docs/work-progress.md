# Project Work Progress & Status Tracker

This document tracks all work items, development milestones, current status, and upcoming tasks for the **Salesforce <-> AWS Integration Platform**.

---

## 📌 Project Overview
- **Goal:** Build a robust, bidirectional integration pipeline between **Live Salesforce** and AWS services (S3, DynamoDB, SQS, Secrets Manager), running in a local Docker development environment with a management UI dashboard.
- **Local Stack:** Docker Compose, MySQL 8.0 (`localhost:3307`), LocalStack 3.8 Community (S3, DynamoDB, SQS, Secrets Manager), Live Salesforce OAuth 2.0 Auth Code Integration Engine (`src/integration-engine`), Vercel Serve Frontend (`src/dashboard-ui`), Python `.venv`.

---

## 📊 Milestone Tracker

| Phase | Milestone / Feature | Status | Completion Date |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Project Inception & Architecture Setup** | 🟢 Complete | 2026-09-05 |
| | - Antigravity ([`AGENTS.md`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/AGENTS.md), [`GEMINI.md`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/GEMINI.md)) instruction setup | 🟢 Complete | 2026-09-05 |
| | - Docs structure & initial ADRs | 🟢 Complete | 2026-09-05 |
| | - Directory scaffolding & Docker configurations | 🟢 Complete | 2026-09-05 |
| **Phase 2** | **Local Infrastructure & Multi-Database Topology** | 🟢 Complete | 2026-09-05 |
| | - LocalStack AWS container (S3, DynamoDB, SQS, Secrets Manager) | 🟢 Complete | 2026-09-05 |
| | - LocalStack Community image pinning (`localstack/localstack:3.8`) | 🟢 Complete | 2026-09-05 |
| | - MySQL 8.0 container with CRM schemas & token management | 🟢 Complete | 2026-09-05 |
| | - Host port conflict resolution for MySQL (`3307:3306`) | 🟢 Complete | 2026-09-05 |
| | - Python Virtual Environment (`.venv`) initialized & dependencies installed | 🟢 Complete | 2026-09-05 |
| **Phase 3** | **OAuth 2.0 Authorization Code Flow & Secrets Manager** | 🟢 Complete | 2026-09-05 |
| | - Salesforce OAuth 2.0 Auth Code flow with Callback URL | 🟢 Complete | 2026-09-05 |
| | - Proof Key for Code Exchange (PKCE / RFC 7636) with SHA-256 S256 Challenge | 🟢 Complete | 2026-09-05 |
| | - AWS Secrets Manager replication for secure Refresh Token storage | 🟢 Complete | 2026-09-05 |
| | - Automated Token Expiration Tracking & Refresh Token Rotation | 🟢 Complete | 2026-09-05 |
| | - Scopes cleaned (removed `id` scope per user request) | 🟢 Complete | 2026-09-05 |
| **Phase 4** | **Web UI Dashboard with Vercel CLI & Direct Live Salesforce Auth** | 🟢 Complete | 2026-09-05 |
| | - Direct Single-Sign-On Salesforce Connection (removed manual user switcher) | 🟢 Complete | 2026-09-05 |
| | - Live Token Expiry countdown timer & one-click OAuth connect | 🟢 Complete | 2026-09-05 |
| | - Replicated AWS Secrets Manager metadata viewer | 🟢 Complete | 2026-09-05 |
| | - All 5 container services tested & verified healthy | 🟢 Complete | 2026-09-05 |
| **Phase 5** | **AI Governance & Continuous Documentation Safeguards** | 🟢 Complete | 2026-09-05 |
| | - Created [`.agents/rules/mandatory-documentation-safeguard.md`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/.agents/rules/mandatory-documentation-safeguard.md) (`always_on`) | 🟢 Complete | 2026-09-05 |
| | - Maintained documentation updates across all turns | 🟢 Complete | 2026-09-05 |
| **Phase 6** | **MySQL CRM Relational Tables (Account, Contact, Opportunity)** | 🟢 Complete | 2026-09-05 |
| | - Created `salesforce_accounts` schema with full CRM attribute mapping | 🟢 Complete | 2026-09-05 |
| | - Created `salesforce_contacts` schema with foreign keys and index optimization | 🟢 Complete | 2026-09-05 |
| | - Created `salesforce_opportunities` schema with stage and amount tracking | 🟢 Complete | 2026-09-05 |
| | - Removed legacy `users` table and static seed users | 🟢 Complete | 2026-09-05 |
| **Phase 7** | **Multi-Target Single Record Sync & Session Isolation** | 🟢 Complete | 2026-09-05 |
| | - Added `POST /api/sync/record` endpoint in [`src/integration-engine/app/main.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/main.py) | 🟢 Complete | 2026-09-05 |
| | - Implemented `sync_single_salesforce_record` in [`src/integration-engine/app/sync_service.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/sync_service.py) | 🟢 Complete | 2026-09-05 |
| | - Added strict per-browser / incognito window `session_id` isolation (`sessionStorage` + `X-Session-ID`) | 🟢 Complete | 2026-09-05 |
| | - Added 401 HTTP authentication enforcement on all backend Salesforce endpoints when session is disconnected | 🟢 Complete | 2026-09-05 |
| | - Added UI client-side connection guards to prevent data leakage in disconnected windows | 🟢 Complete | 2026-09-05 |
| | - Fixed MySQL Synced DB table viewer response parsing (`records` array) | 🟢 Complete | 2026-09-05 |
| | - Tested and verified session isolation across incognito and authenticated windows | 🟢 Complete | 2026-09-05 |
| **Phase 8** | **Universal Zero-Trust Disconnected Data Guard** | 🟢 Complete | 2026-09-06 |
| | - Global `require_authenticated_salesforce_session` guard on all MySQL, AWS & Audit endpoints | 🟢 Complete | 2026-09-06 |
| | - Total lockout of MySQL records, DynamoDB items, S3 archives, SQS queues, Secrets & Logs when disconnected | 🟢 Complete | 2026-09-06 |
| | - Zero data leakage guarantee across unauthenticated browser windows and tabs | 🟢 Complete | 2026-09-06 |
| **Phase 9** | **Live Volume Mounting & Instant Hot-Reloading** | 🟢 Complete | 2026-09-06 |
| | - Mounted `./src/integration-engine/app:/app/app` with Uvicorn `--reload` in [`docker-compose.yml`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docker-compose.yml) | 🟢 Complete | 2026-09-06 |
| | - Mounted `./src/dashboard-ui:/app` for instant frontend updates without container rebuilds | 🟢 Complete | 2026-09-06 |
| **Phase 10** | **Modern Glassmorphic Toast Notification Engine** | 🟢 Complete | 2026-09-06 |
| | - Designed and integrated dynamic stacking toast container in [`src/dashboard-ui/index.html`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/index.html) | 🟢 Complete | 2026-09-06 |
| | - Built `showToast(msg, type, duration)` supporting `success`, `error`, `warning`, and `info` with smooth slide-in & auto-dismiss | 🟢 Complete | 2026-09-06 |
| | - Replaced 100% of intrusive browser `alert()` popups across the dashboard with non-blocking modern toasts | 🟢 Complete | 2026-09-06 |

---

## 📝 Activity Log

### 2026-09-06
- **Asynchronous First-Time Screen Load Connection Check & Auto-Data Hydration:**
  - Diagnosed un-awaited `checkHealth()` asynchronous promise race during initial `refreshAll()` boot on `DOMContentLoaded`.
  - Converted `refreshAll()` to an `async` function and ensured `await checkHealth()` evaluates the live session state from `/api/status` with `X-Session-ID` before deciding to render locked states or hydrate CRM/AWS tables.
  - Automatically loads the active tab's data (Live Salesforce records, MySQL DB, AWS DynamoDB, S3 files, SQS metrics) on initial screen load and page refresh whenever an authenticated session exists.
- **Implemented Modern Glassmorphic Toast Notification Engine:**
  - Added `#toast-container` and CSS transition keyframe styling to [`src/dashboard-ui/index.html`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/index.html).
  - Implemented `showToast()` and `dismissToast()` in [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js) with support for 4 notification types (`success`, `error`, `warning`, `info`), FontAwesome iconography, and cubic-bezier slide transitions.
  - Replaced all 24 occurrences of native synchronous browser `alert()` calls with `showToast()`, including OAuth actions, single-record syncs, full sync pipelines, AWS-to-Salesforce push, S3 clipboard actions, and disconnected warnings.
  - Installed a global `window.alert` wrapper fallback to guarantee no future browser dialog blocks the UI.
- **Resolved MySQL `salesforce_oauth_tokens` Schema & Legacy `user_id` Constraint:**
  - Diagnosed MySQL Error 1364 (`Field 'user_id' doesn't have a default value`) triggered during OAuth callback token insertion into `salesforce_oauth_tokens`.
  - Dropped foreign key constraint `salesforce_oauth_tokens_ibfk_1`, dropped composite index `idx_user_active`, and dropped legacy column `user_id` from the running MySQL container.
  - Added automated migration in [`src/integration-engine/app/database.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/database.py) (`init_db()`) to safely drop `user_id` and associated foreign keys on startup.
- **Resolved MySQL `salesforce_oauth_tokens.session_id` Column Migration:**
  - Applied `ALTER TABLE salesforce_oauth_tokens ADD COLUMN session_id VARCHAR(100) NULL AFTER id, ADD INDEX idx_session_id(session_id)` to running MySQL container.
  - Added automated database startup migration in [`src/integration-engine/app/database.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/database.py) using SQLAlchemy `init_db()` inspection.
  - Updated [`src/scripts/init-mysql.sql`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/scripts/init-mysql.sql) to remove deprecated `users` table and ensure clean initialization.
- **Configured Live Volume Mounting & Instant Hot-Reloading:**
  - Added `./src/integration-engine/app:/app/app` volume mount and `uvicorn --reload` to [`docker-compose.yml`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docker-compose.yml) and [`src/integration-engine/Dockerfile`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/Dockerfile). All Python code edits now reload in Docker in real-time.
  - Added `./src/dashboard-ui:/app` volume mount to [`docker-compose.yml`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docker-compose.yml). All frontend HTML, CSS, and JS edits now reflect immediately upon browser refresh without rebuilding containers.
- **Implemented Universal Zero-Trust Disconnected Data Guard:**
  - Added FastAPI dependency [`require_authenticated_salesforce_session`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/main.py) to all data inspection endpoints (`/api/db/accounts`, `/api/db/contacts`, `/api/db/opportunities`, `/api/aws/dynamodb/records`, `/api/aws/s3/files`, `/api/aws/s3/file`, `/api/aws/sqs/stats`, `/api/secrets`, `/api/logs`, `/api/sync/salesforce-to-aws`, `/api/sync/aws-to-salesforce`, `/api/sync/record`).
  - Added automatic 401 Unauthorized returns when no active, valid Salesforce session is present.
  - Updated [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js) with `renderLockedStateForAllTabs()` and global `isSalesforceConnected` state tracking, instantly zeroing and locking every dashboard tab (Salesforce Live, MySQL DB, AWS DynamoDB, AWS S3, AWS SQS, Secrets Manager, and Audit Logs) whenever Salesforce is disconnected.
  - Updated initial HTML placeholders in [`src/dashboard-ui/index.html`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/index.html) to show locked state placeholders prior to authentication.
  - **Dynamic Navigation Tab Protection:** Configured `#tab-btn-sync` to be hidden when not logged in to Salesforce, automatically rerouting any unauthenticated access to the live CRM explorer and displaying the sync tab only when an active Salesforce session is authenticated.

### 2026-09-05
- **Initialized project workspace & established `docs/` hub:** Created `work-progress.md`, `discussions-and-decisions.md`, `architecture.md`, and `setup-guide.md`.
- **Configured LocalStack Community & MySQL:** Pinned `localstack/localstack:3.8` with `ACTIVATE_PRO=0`. Mapped MySQL to host port `3307`.
- **Loaded Live Salesforce OAuth Credentials:** Re-created `integration-engine` with updated `.env` credentials.
- **Removed `id` Scope:** Updated `SALESFORCE_SCOPES` to `api refresh_token offline_access`.
- **Provided `redirect_uri_mismatch` Resolution:** Documented Callback URL troubleshooting steps.
- **Implemented PKCE (RFC 7636) Extension:** Added cryptographic `code_verifier` generator, SHA-256 `code_challenge` (S256), state session management, and `code_verifier` payload parameter in token exchange endpoint.
- **Implemented MySQL CRM Tables (Account, Contact, Opportunity):** Added SQLAlchemy models in [`src/integration-engine/app/database.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/database.py), updated [`src/scripts/init-mysql.sql`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/scripts/init-mysql.sql), integrated automated upsert pipeline in [`src/integration-engine/app/sync_service.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/sync_service.py), and added inspection endpoints in [`src/integration-engine/app/main.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/main.py).
- **Removed Custom Users Table & Seed Users:** Removed `users` table and static seed records (`lead_developer`, `crm_administrator`). Replaced with 1:1 Live Salesforce authentication.
- **Implemented Multi-Target Single Record Sync:** Implemented `POST /api/sync/record` to mirror individual Salesforce records to MySQL (`salesforce_accounts`/`contacts`/`opportunities`), DynamoDB (`SalesforceSyncRecords`), and S3 (`salesforce-raw-events`).
- **Implemented Browser / Incognito Session Isolation & Strict Connection Enforcement:** Added `session_id` column, enforced strict session validation in `get_valid_token`, added 401 Unauthorized protection on all Salesforce API routes, and added client-side connection guards in [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js).
- **Compiled Complete URL & API Endpoint Catalog:** Updated [`docs/setup-guide.md`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docs/setup-guide.md) with comprehensive listings of all Web UI, Swagger/OpenAPI, REST API, MySQL, and LocalStack endpoints.
