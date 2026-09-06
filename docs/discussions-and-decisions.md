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

### Session 27: Secrets Manager OAuth Refresh Token ARN Resolution & Rotation Fix
- Inspected MySQL `salesforce_oauth_tokens` table and LocalStack AWS Secrets Manager.
- Found that the refresh token was present in AWS Secrets Manager, but token retrieval failed due to `refresh_token_secret_arn.split(":")[-1]` in [`src/integration-engine/app/oauth_service.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/oauth_service.py).
- The split operation stripped the `arn:aws:...:secret:` prefix, leaving `salesforce/<session_id>/refresh_token-vjYTFg` (which included the 6-character random suffix generated by AWS/LocalStack). AWS Secrets Manager rejected this identifier as neither a valid ARN nor an exact secret name.
- Fixed `oauth_service.py` to pass the complete secret ARN directly to `secrets_manager.get_secret()` and `delete_secret()`, with automatic fallback to `salesforce/{session_id}/refresh_token`.
- Tested and verified live token rotation via `POST /api/auth/salesforce/refresh`.

### Session 28: Salesforce Record ID Hyperlinks & Deep-Linking
- User requested that Salesforce IDs displayed across the dashboard be clickable hyperlinks pointing directly to the live records in Salesforce.
- Implemented `getSalesforceRecordUrl(recordId)` and `renderSalesforceIdLink(recordId)` in [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js).
- Deep-links use the user's active `instanceUrl` (e.g., `${instanceUrl}/${recordId}`) opening in a new tab (`target="_blank"` with `rel="noopener noreferrer"`).
- Applied hyperlinks across the Live Salesforce CRM Explorer, MySQL Synced Database table, and AWS DynamoDB table.
- Also hyperlinked the Salesforce Instance URL in the active session status card.

### Session 29: Admin Custom Field Mapping & Dynamic Query Studio
- User requested an admin studio where end users can define custom field mappings, set SOQL filters/preferences, pull live Salesforce data on-demand, and display mapped results in a responsive data table.
- **Architectural Decision (ADR-015):**
  - Use Salesforce Describe REST API (`/services/data/vXX.X/sobjects/{sobject}/describe`) to dynamically introspect available standard and custom fields with their data types.
  - Provide a persistent profile store via MySQL `salesforce_custom_mappings` table (`selected_fields`, `field_mappings`, `filter_clause`, `sort_field`, `sort_order`, `record_limit`).
  - Support on-demand SOQL generation and mapping transformations in [`src/integration-engine/app/main.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/main.py) returning both mapped clean attributes and raw payloads.
  - Built an interactive Studio in [`src/dashboard-ui/index.html`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/index.html) and [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js) with real-time field filtering, editable target column aliases, SOQL preview, and JSON/CSV data export.

### ADR-016: Dynamic MySQL Schema Introspection & On-Demand Column Provisioning for Admin Mapping
- **Date:** 2026-09-06
- **Status:** Accepted
- **Decision:**
  - Expose `GET /api/db/schema-for-sobject/{sobject}` to introspect target MySQL table columns from `information_schema.columns` and auto-provision dynamic tables for new sObjects.
  - Expose `POST /api/db/add-column` to dynamically execute `ALTER TABLE <table_name> ADD COLUMN <sanitized_column_name> <data_type> NULL` with strict SQL identifier sanitization and whitelist validation for SQL data types (`VARCHAR`, `TEXT`, `INT`, `DECIMAL`, `DATETIME`, `BOOLEAN`).
  - Upgrade the Admin Custom Mapping Studio to present a smart dropdown of existing MySQL columns for each Salesforce field, with an inline "+ Add New Column to MySQL..." modal workflow that automatically provisions the new database column and maps it to the selected Salesforce field.

---

### Session 31: MySQL Field Mapping & Dynamic Column Creation in Admin Studio
- **User Requirement:** "for 'Custom Target Column Alias' show mysql field for mapping and if user want we can create a new field in mysql"
- **Implementation & Resolution:**
  1. **Backend Endpoints:**
     - Created `get_table_name_for_sobject(sobject)` to map standard and custom sObjects to corresponding MySQL tables (`salesforce_accounts`, `salesforce_contacts`, `salesforce_opportunities`, `salesforce_leads`, etc.).
     - Added `GET /api/db/schema-for-sobject/{sobject}` in [`src/integration-engine/app/main.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/main.py) to return existing columns and data types.
     - Added `POST /api/db/add-column` with regex sanitization (`re.sub(r'[^a-zA-Z0-9_]', '_', name).lower().strip('_')`), type validation against allowed SQL types, and `ALTER TABLE` execution.
  2. **Frontend UI & Modal:**
     - Added target MySQL table badge (`#studio-mysql-table-badge`) and `+ New DB Field` button in Step 2 of [`src/dashboard-ui/index.html`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/index.html).
     - Built modal dialog `#add-mysql-column-modal` with live SQL name preview, data type selector (`VARCHAR(255)`, `TEXT`, `INT`, `DECIMAL(18,2)`, `DATETIME`, `BOOLEAN`), and auto-mapping checkbox.
  3. **Mapping Dropdown & Auto-Matching:**
     - Updated `renderStudioFieldsList()` in [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js) to render a dropdown populated with MySQL columns, action triggers (`➕ + Add New Field to MySQL...`, `✏️ Enter Custom Alias...`), and a direct `+` quick button.
     - Built automatic snake_case matching (e.g., `BillingCity` matches `billing_city`).
     - Verified end-to-end dynamically adding columns and executing custom queries with mapped columns.

---

### Session 32: Enhanced Dropdown-Like Options for MySQL Target Mapping
- **User Requirement:** "MySQL Target Column / Alias" field are needed to be drop down like options
- **Implementation & Resolution:**
  - Upgraded `<select>` styling in [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js) with distinct optgroup dividers (`── 🗄️ MySQL Columns (${studioMysqlTable}) ──` and `── ⚡ Actions ──`).
  - Added visual icon indicators for all options (`⚙️ Default`, `🔹 MySQL Column (type)`, `➕ + Add New Field to MySQL...`, `✏️ Enter Custom Alias...`).
  - Sorted MySQL database columns alphabetically for intuitive searching and browsing.
  - Retained the inline quick `➕` button for immediate modal popup.

---

### Session 33: Removed "+ New DB Field" Button from Header Toolbar
- **User Requirement:** remove "+ New DB Field" button
- **Implementation & Resolution:**
  - Removed the "+ New DB Field" button from the Step 2 toolbar in [`src/dashboard-ui/index.html`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/index.html) to keep the header clean and focused on field filtering and selection.
  - Database column creation remains fully accessible via the dropdown option `➕ + Add New Field to MySQL...` and inline row action buttons.

---

### Session 34: Single-Column Full-Width Studio Layout & On-Demand Live Pulled Data Screen
- **User Requirement:** "make 'live pulled data' as on demand screen whenever some run query and even then open it end of the oage after filter compoenet so and extend all mapping compoenent to so it became one column page"
- **Implementation & Resolution:**
  - Restructured Admin Mapping Studio in [`src/dashboard-ui/index.html`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/index.html) from a two-column 5/7 grid into a sequential single-column full-width experience.
  - Extended all cards (Step 1 sObject Selection, Step 2 Field Mapping, Step 3 Filters & Preferences) to full container width.
  - Positioned the `#studio-results-section` below Step 3 in an initially hidden state.
  - Updated `executeStudioCustomQuery()` in [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js) to reveal `#studio-results-section` and smoothly scroll it into view upon query execution.
  - Added a "Hide" action button in the results header allowing users to collapse the pulled data view on demand.

---

### Session 35: Non-Scrollable Field Selection & MySQL Mapping Component
- **User Requirement:** "Field Selection & MySQL Mapping this component is scrollable i want it to be non scrollable"
- **Implementation & Resolution:**
  - Removed `max-h-[380px]` and `overflow-y-auto` from the `#mapping-fields-container` in [`src/dashboard-ui/index.html`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/index.html).
  - The Field Selection & MySQL Mapping component now expands to its full natural height, removing internal nested scrollbars.

---

### Session 36: Inline `+` Button Removal & Full-Width Dropdown Refinement
- **User Requirement:** "now the + icon got hidden i want you to remove this button and make nothing got hide"
- **Implementation & Resolution:**
  - Removed the inline `+` button next to the dropdown in [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js) to prevent horizontal layout squishing and hidden elements.
  - Widened the dropdown selector (`w-72 sm:w-80 md:w-96`) and streamlined row alignments so all labels, badges, and options are visible with zero clipping.
  - Database column addition remains accessible directly within the dropdown options via `➕ + Add New Field to MySQL...`.
