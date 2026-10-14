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
| **Phase 11** | **Direct Salesforce Record ID Deep-Linking & Hyperlinks** | 🟢 Complete | 2026-09-06 |
| | - Implemented `getSalesforceRecordUrl()` and `renderSalesforceIdLink()` in [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js) | 🟢 Complete | 2026-09-06 |
| | - Linked all Salesforce Record IDs in Live Salesforce Explorer, MySQL Synced DB, and AWS DynamoDB tables to open live Salesforce records in new browser tabs | 🟢 Complete | 2026-09-06 |
| | - Hyperlinked instance URL in the active session card | 🟢 Complete | 2026-09-06 |
| **Phase 12** | **Admin Custom Field Mapping & Query Studio** | 🟢 Complete | 2026-09-06 |
| | - Implemented Live Salesforce Describe API metadata fetcher (`GET /api/salesforce/describe/{sobject}`) | 🟢 Complete | 2026-09-06 |
| | - Created MySQL `salesforce_custom_mappings` table for persistent profile management | 🟢 Complete | 2026-09-06 |
| | - Built custom query engine (`POST /api/salesforce/custom-query`) with field mapping, filters, sorting & limits | 🟢 Complete | 2026-09-06 |
| | - Built Admin Studio UI with interactive field selector, mapping aliases, live data grid, and JSON/CSV export | 🟢 Complete | 2026-09-06 |
| **Phase 13** | **MySQL Dynamic Field Mapping & On-Demand Column Studio** | 🟢 Complete | 2026-09-06 |
| | - Implemented `GET /api/db/schema-for-sobject/{sobject}` for dynamic schema inspection & auto-table creation | 🟢 Complete | 2026-09-06 |
| | - Implemented `POST /api/db/add-column` with SQL sanitization & data type validation (`ALTER TABLE ADD COLUMN`) | 🟢 Complete | 2026-09-06 |
| | - Integrated MySQL column dropdowns with sObject schema mapping and intelligent snake_case matching | 🟢 Complete | 2026-09-06 |
| | - Added interactive "Add Column to MySQL Table" modal with live SQL name preview & auto-mapping | 🟢 Complete | 2026-09-06 |
| **Phase 14** | **Salesforce DX (`force-app`) Source Structure Setup** | 🟢 Complete | 2026-10-14 |
| | - Generated standard Salesforce DX directory structure under [`force-app/main/default`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/force-app/main/default) | 🟢 Complete | 2026-10-14 |
| | - Added project manifest [`manifest/package.xml`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/manifest/package.xml) (API v67.0) | 🟢 Complete | 2026-10-14 |
| | - Configured [`sfdx-project.json`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/sfdx-project.json) and [`.forceignore`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/.forceignore) | 🟢 Complete | 2026-10-14 |
| | - Configured scratch org definition [`config/project-scratch-def.json`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/config/project-scratch-def.json) and script templates | 🟢 Complete | 2026-10-14 |
| **Phase 15** | **Media Type Account Search, SOQL & Cypher Query Engine** | 🟢 Complete | 2026-10-14 |
| | - Added "Search All Media Type of Account" one-click search button in Live Salesforce Explorer | 🟢 Complete | 2026-10-14 |
| | - Added text search filter bar with live debounce and query execution | 🟢 Complete | 2026-10-14 |
| | - Added dynamic openCypher / Neo4j query translator (`sf_client.to_cypher`) in integration engine | 🟢 Complete | 2026-10-14 |
| | - Added backend query parameters `search` and `media_only` to `GET /api/salesforce/records/{sobject}` | 🟢 Complete | 2026-10-14 |
| | - Integrated Cypher query generation and return in `POST /api/salesforce/custom-query` | 🟢 Complete | 2026-10-14 |
| | - Created interactive "Salesforce SOQL & Cypher Query Inspector" modal with syntax copying | 🟢 Complete | 2026-10-14 |
| | - Added SOQL / Cypher view toggle in Admin Query Studio executed snippet bar | 🟢 Complete | 2026-10-14 |
| | - Added quick query presets in Admin Query Studio including "Search All Media Type of Account" | 🟢 Complete | 2026-10-14 |
| | - Added purple Media badges in account table rows for accounts with Type or Industry set to Media | 🟢 Complete | 2026-10-14 |
| | - Added zero-results fallback with 1-click sample Media Account creation in Live Salesforce | 🟢 Complete | 2026-10-14 |
| | - Created dedicated query files: [`scripts/salesforce/cypher/account.cypher`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/scripts/salesforce/cypher/account.cypher) and [`scripts/salesforce/soql/media_accounts.soql`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/scripts/salesforce/soql/media_accounts.soql) | 🟢 Complete | 2026-10-14 |
| **Phase 16** | **NLP Natural Language Query Parser Engine & Interactive Chips** | 🟢 Complete | 2026-10-14 |
| | - Created [`src/integration-engine/app/nlp_query_service.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/nlp_query_service.py) for entity & intent extraction | 🟢 Complete | 2026-10-14 |
| | - Added endpoint `POST /api/salesforce/nlp-query` returning parsed SOQL, Cypher & interpretation | 🟢 Complete | 2026-10-14 |
| | - Added interactive NLP query chips and Run NLP execution button in Live Salesforce Explorer | 🟢 Complete | 2026-10-14 |
| | - Added dynamic NLP interpretation badge (`#sf-filter-nlp-badge`) displaying parsed intent in UI | 🟢 Complete | 2026-10-14 |

---

## 📝 Activity Log

### 2026-10-14
- **Implemented Natural Language (NLP) Query Engine for Media Accounts & sObjects:**
  - **User Requirement:** "Search All Media Type of Account" this NLP query that should need to work like this it should get all accounts with media type.
  - **NLP Engine Architecture ([`src/integration-engine/app/nlp_query_service.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/nlp_query_service.py)):**
    - Built `NLPQueryService.parse_nlp_query(query_text)` to dynamically parse natural language queries.
    - Accurately recognizes queries like `"Search All Media Type of Account"`, `"Get all accounts with media type"`, `"Show media accounts"`, and extracts:
      - Target entity: `Account`.
      - Target criteria: `Type = 'Media' OR Industry = 'Media' OR Type LIKE '%Media%' OR Industry LIKE '%Media%' OR Name LIKE '%Media%'`.
      - OpenCypher Graph representation: `MATCH (a:Account) WHERE (a.Type = 'Media' ...) RETURN ...`.
      - Human-readable interpretation summary: `"Identified criteria: Account Type or Industry matches 'Media'"`.
  - **API & Engine Integration ([`src/integration-engine/app/main.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/main.py)):**
    - Added `POST /api/salesforce/nlp-query` taking `NLPQueryPayload(query, limit)`.
    - Integrated NLP parsing directly into `get_salesforce_records` so any NLP query entered in the search bar is dynamically translated.
    - Returns `interpretation` metadata alongside records, SOQL, and Cypher queries.
  - **Dashboard UI NLP Enhancements ([`src/dashboard-ui/index.html`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/index.html) & [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js)):**
    - Updated search toolbar with NLP placeholder, gradient "Run NLP" action button, and interactive NLP prompt chips (`"Search All Media Type of Account"`, `"Get all accounts with media type"`, `"Show all technology accounts"`).
    - Added green NLP interpretation badge displaying how the query was parsed.
    - Auto-switches target entity dropdown to `Account` when an account/media NLP query is entered.
- **Implemented "Search All Media Type of Account" & SOQL / Cypher Query Engine:**
  - **User Requirement:** Add UI search option "Search All Media Type of Account" that returns and shows all Media Related Accounts, with Cypher and SOQL query support.
  - **Backend Integration Engine Updates ([`src/integration-engine/app/salesforce_client.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/salesforce_client.py) & [`src/integration-engine/app/main.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/main.py)):**
    - Extended `SalesforceClient.get_records` with `search: Optional[str]` and `media_only: Optional[bool]`.
    - Added `SalesforceClient.to_cypher` to generate graph-compliant openCypher queries for Neo4j, Memgraph, and AWS Neptune.
    - Updated endpoint `GET /api/salesforce/records/{sobject}` to accept `search` and `media_only` query parameters and return executed `soql` and `cypher` queries.
    - Updated `POST /api/salesforce/custom-query` to return both `soql` and `cypher` query strings for live introspection.
  - **Dashboard UI Enhancements ([`src/dashboard-ui/index.html`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/index.html) & [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js)):**
    - Added a search input and primary action button **"Search All Media Type of Account"** in the Live Salesforce sObject Explorer toolbar.
    - Added active filter notification bar with matching record count and quick "Copy SOQL" / "Copy Cypher" buttons.
    - Added visual badges highlighting Media accounts with purple pill indicators (`<i class="fa-solid fa-photo-film"></i> Media`).
    - Added empty state handler with one-click "Create Sample Media Account (Universal Media Group Inc)" to verify in live orgs lacking Media data.
    - Added "Salesforce SOQL & Cypher Query Inspector" modal (`#query-inspector-modal`) displaying side-by-side formatted queries with clipboard copy.
    - Added "Search All Media Type of Account" quick preset button in Admin Query Studio (Step 3).
    - Upgraded Executed Query bar in Query Studio to toggle between SOQL and Cypher representation.
  - **Query Artifacts Created:**
    - [`scripts/salesforce/cypher/account.cypher`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/scripts/salesforce/cypher/account.cypher): OpenCypher queries for matching Media Accounts and traversing connected Contact / Opportunity nodes.
    - [`scripts/salesforce/soql/account.soql`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/scripts/salesforce/soql/account.soql): Updated with Media search query clause.
    - [`scripts/salesforce/soql/media_accounts.soql`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/scripts/salesforce/soql/media_accounts.soql): Dedicated SOQL query script.
- **Initialized Standard Salesforce DX (`force-app`) Structure & Tooling Suite:**
  - Scaffolding created for Salesforce DX source-format directory structure under `force-app/main/default/`:
    - `classes`, `triggers`, `lwc`, `aura`, `objects`, `permissionsets`, `tabs`, `flexipages`, `layouts`, `applications`, `staticresources`, `contentassets`.
  - Removed placeholder `.gitkeep` files from `force-app/` per user request, keeping metadata folders clean for incoming Salesforce components.
  - Added full Salesforce DX developer tooling configuration files from template:
    - Code quality & formatting: [`eslint.config.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/eslint.config.js), [`jest.config.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/jest.config.js), [`.prettierrc`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/.prettierrc), [`.prettierignore`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/.prettierignore), [`package.json`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/package.json), and [`.husky/`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/.husky/).
    - VS Code configurations: [`.vscode/extensions.json`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/.vscode/extensions.json), [`.vscode/launch.json`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/.vscode/launch.json), and updated [`.vscode/settings.json`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/.vscode/settings.json).
  - Added project descriptor [`sfdx-project.json`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/sfdx-project.json) set to `packageDirectories: [{"path": "force-app", "default": true}]` with `sourceApiVersion: "67.0"`.
  - Added metadata manifest [`manifest/package.xml`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/manifest/package.xml) covering Apex classes, triggers, Aura, LWC, and static resources.
  - Added scratch org definition [`config/project-scratch-def.json`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/config/project-scratch-def.json).
  - Added [`.forceignore`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/.forceignore) and updated root [`.gitignore`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/.gitignore) to exclude `.sf/` and `.sfdx/` CLI cache.
  - Added sample SOQL and Apex execution scripts under [`scripts/salesforce/`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/scripts/salesforce/).

### 2026-10-07
- **Investigated Salesforce Authorization URL & External Client App `EC_` Error Resolution:**
  - Inspected OAuth 2.0 PKCE authorization URL generation in [`src/integration-engine/app/oauth_service.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/oauth_service.py) (`get_authorization_url`) and endpoint `GET /api/auth/salesforce/login`.
  - Diagnosed root causes for Salesforce error `EC_ is not found in the organisation` (Salesforce External Client App domain mismatch, developer name vs consumer key mixup, packaged vs local distribution state).
  - Updated [`docs/setup-guide.md`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docs/setup-guide.md) with troubleshooting guide for External Client App setup.
  - Recorded findings in [`docs/discussions-and-decisions.md`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docs/discussions-and-decisions.md).
- **Inspected Salesforce Org Domain URLs Across Local Environments:**
  - Checked currently active container environment variables and `.env` (`SALESFORCE_LOGIN_URL=https://login.salesforce.com`).
  - Enumerated local Salesforce CLI authenticated org profiles from `~/.sfdx/` to identify potential target sandbox and developer org instance URLs.


- **Removed Inline `+` Button from Mapping Rows & Streamlined Dropdown Layout:**
  - Removed the inline `+` icon button next to mapping dropdowns in [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js) to eliminate visual clipping and horizontal overflow.
  - Expanded the `<select>` dropdown width (`w-72 sm:w-80 md:w-96`) to ensure long column names and type annotations are fully legible with zero truncation.
  - Retained `➕ + Add New Field to MySQL...` directly within the dropdown options to trigger the creation modal seamlessly.
- **Made Field Selection & MySQL Mapping Component Non-Scrollable:**
  - Removed internal fixed height and nested scrollbar (`max-h-[380px] overflow-y-auto`) from `#mapping-fields-container` in [`src/dashboard-ui/index.html`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/index.html).
  - Component now renders at its full natural height without inner scrolling, providing seamless vertical reading across all fields.
- **Refactored Admin Mapping Studio to Full-Width Single-Column Flow with On-Demand Results:**
  - Converted the Admin Custom Mapping Studio from a split 2-column grid into a spacious full-width 1-column layout in [`src/dashboard-ui/index.html`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/index.html).
  - Extended sObject Selection (Step 1), Field Selection & MySQL Mapping (Step 2), and Filter/Sort/Limit Preferences (Step 3) across the full viewport width.
  - Positioned the "Live Pulled Data" results screen at the bottom of the page (after Step 3) in an initially collapsed/hidden state.
  - Updated `executeStudioCustomQuery()` in [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js) to dynamically unhide and smoothly scroll down to the Live Pulled Data grid upon query execution.
  - Added a "Hide" button to easily collapse the results section when finished.
- **Removed "+ New DB Field" Toolbar Button:**
  - Removed redundant "+ New DB Field" button from the Step 2 toolbar in [`src/dashboard-ui/index.html`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/index.html), streamlining the field selection header to keep database provisioning directly accessible via the dropdown options.
- **Enhanced MySQL Target Column Dropdown Options & Alphabetical Ordering:**
  - Upgraded target mapping dropdown in [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js) with clear visual icon markers (`🔹`, `⚙️`, `➕`, `✏️`), categorized optgroups (`MySQL Columns` vs `Actions`), alphabetical sorting, and hover highlights.
- **Implemented MySQL Dynamic Field Mapping & On-Demand Column Studio:**
  - Added `GET /api/db/schema-for-sobject/{sobject}` in [`src/integration-engine/app/main.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/main.py) to inspect local MySQL tables (e.g. `salesforce_accounts`, `salesforce_contacts`) and automatically provision dynamic tables for custom/standard objects.
  - Added `POST /api/db/add-column` with regex sanitization (`re.sub(r'[^a-zA-Z0-9_]', '_', name)`), allowed data type validation (`VARCHAR(255)`, `TEXT`, `INT`, `DECIMAL(18,2)`, `DATETIME`, etc.), and live `ALTER TABLE` execution.
  - Upgraded Admin Mapping Studio in [`src/dashboard-ui/index.html`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/index.html) and [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js) with:
    1. Interactive target MySQL column `<select>` populated from database schema.
    2. One-click `➕ + Add New Field to MySQL...` inline button and action dropdown.
    3. Modal dialog (`#add-mysql-column-modal`) for on-demand column creation with live SQL name preview, data type selector, and automatic mapping toggle.
    4. Auto-mapping of standard Salesforce fields to matching MySQL columns (e.g. `BillingCity` -> `billing_city`).
- **Resolved Admin Studio Initial Placeholder State & 401 Session Lifecycle:**
  - Diagnosed issue where the Admin Studio data grid table retained the initial locked placeholder after authenticating and switching tabs.
  - Updated `initAdminMappingStudio()` in [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js) to re-render the clean "Ready to Pull Custom Data" state (or last query results) whenever an authenticated Salesforce session is present.
  - Added strict 401 response handling to `fetchSobjectSchema()` and `executeStudioCustomQuery()`.
- **Built Admin Custom Field Mapping & Query Studio:**
  - Implemented `describe_sobject()` in [`src/integration-engine/app/salesforce_client.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/salesforce_client.py) to dynamically inspect live sObject fields and data types from Salesforce.
  - Created `salesforce_custom_mappings` table in [`src/integration-engine/app/database.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/database.py) and [`src/scripts/init-mysql.sql`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/scripts/init-mysql.sql).
  - Added REST API endpoints in [`src/integration-engine/app/main.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/main.py):
    - `GET /api/salesforce/describe/{sobject}` - Live field metadata inspection
    - `POST /api/salesforce/custom-query` - Dynamic SOQL query with custom field mappings and filters
    - `GET / POST / PUT / DELETE /api/admin/mappings` - Full CRUD profile management
  - Designed responsive two-column Admin Studio in [`src/dashboard-ui/index.html`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/index.html) and implemented complete client logic in [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js) with live field selection, alias mapping, SOQL preview, interactive data grid, and JSON/CSV file exports.
- **Direct Salesforce Record ID Deep-Linking & Hyperlinks:**
  - Implemented `getSalesforceRecordUrl()` and `renderSalesforceIdLink()` in [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js) using the authenticated `currentSalesforceInstanceUrl`.
  - Replaced plain text Salesforce ID displays with clickable external hyperlinks with icon indicators (`target="_blank"`, `rel="noopener noreferrer"`) across:
    1. **Live Salesforce CRM Explorer** (`loadSalesforceRecords`)
    2. **MySQL Synced Database Table** (`loadMySQLRecords`)
    3. **AWS DynamoDB Table** (`loadDynamoDBRecords`)
    4. **Active Salesforce Session Card** (Instance URL link)
- **Fixed Secrets Manager Secret ID / ARN Resolution for OAuth Token Refresh:**
  - Diagnosed `refresh_token_secret_arn.split(":")[-1]` bug in [`src/integration-engine/app/oauth_service.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/oauth_service.py) which stripped the AWS ARN prefix leaving the random hash suffix (`salesforce/.../refresh_token-vjYTFg`), causing AWS Secrets Manager `ResourceNotFoundException`.
  - Updated `refresh_active_token()` and `disconnect()` to pass the full `token_record.refresh_token_secret_arn` directly to `secrets_manager.get_secret()` and `delete_secret()`, with automatic fallback to session-friendly secret name `salesforce/{session_id}/refresh_token`.
  - Verified live token rotation via `POST /api/auth/salesforce/refresh` against running Docker containers; verified new expiration timestamp (`expires_at`) and `last_refreshed_at` in MySQL database.
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

| **Phase 12** | **Multi-Object NLP Search & openCypher Graph Engine** | 🟢 Complete | 2026-10-15 |
| | - Created [`src/integration-engine/app/nlp_query_service.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/nlp_query_service.py) supporting all sObjects (`Account`, `Contact`, `Opportunity`, `Lead`) | 🟢 Complete | 2026-10-15 |
| | - Multi-entity detection, job titles, deal stages, revenue thresholds, lead statuses, email/phone criteria | 🟢 Complete | 2026-10-15 |
| | - Automated dual-engine query generation (Salesforce SOQL + openCypher for Neo4j / Neptune) | 🟢 Complete | 2026-10-15 |
| | - Unified search in [`src/integration-engine/app/salesforce_client.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/salesforce_client.py) and [`src/integration-engine/app/main.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/main.py) with `context_sobject` | 🟢 Complete | 2026-10-15 |
| | - Dynamic NLP prompt chips per sObject in [`src/dashboard-ui/index.html`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/index.html) and [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js) | 🟢 Complete | 2026-10-15 |
| | - Auto-switching entity selector when cross-object NLP queries are detected | 🟢 Complete | 2026-10-15 |
| | - Rich multi-object table row rendering (Title/Email/Phone, StageName/Amount/Probability, Status/Company) | 🟢 Complete | 2026-10-15 |
| | - Query Inspector modal with copyable SOQL & openCypher queries and real-time NLP interpretation notes | 🟢 Complete | 2026-10-15 |
| | - Created query reference files: [`scripts/salesforce/cypher/account.cypher`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/scripts/salesforce/cypher/account.cypher) and [`scripts/salesforce/soql/media_accounts.soql`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/scripts/salesforce/soql/media_accounts.soql) | 🟢 Complete | 2026-10-15 |

---

## 📅 Daily Activity Log

### 2026-10-15
- **Multi-Object Natural Language (NLP) Search Engine:**
  - Implemented [`src/integration-engine/app/nlp_query_service.py`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/integration-engine/app/nlp_query_service.py) supporting all primary Salesforce sObjects (`Account`, `Contact`, `Opportunity`, `Lead`).
  - Implemented intelligent attribute extraction:
    - **Contact:** Job titles (VP, Director, Manager, Executive, Engineer), email domains (Gmail), contact info presence, and media roles.
    - **Opportunity:** Deal stages (`Closed Won`, `Closed Lost`, `Prospecting`), revenue/deal sizes (`> $50k`, `$100k+`), and active pipeline filtering.
    - **Lead:** Lead statuses (`Qualified`, `Open - Not Contacted`), media industry leads, and contact criteria.
    - **Account:** Media types (`Type = 'Media' OR Industry = 'Media'`), industry filters (`Technology`), annual revenue thresholds (`>= $1M`), and billing geography (`California`).
  - Added bidirectional cross-object entity detection: queries explicitly naming an entity (e.g. "Closed Won deals" typed while on Account tab) automatically route to the correct target sObject.
- **Dual-Engine Query Compilation (Salesforce SOQL + openCypher):**
  - Integrated simultaneous compilation of Salesforce SOQL and openCypher (Neo4j / Memgraph / AWS Neptune) graph queries for every search.
  - Saved reusable query files: [`scripts/salesforce/cypher/account.cypher`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/scripts/salesforce/cypher/account.cypher), [`scripts/salesforce/soql/media_accounts.soql`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/scripts/salesforce/soql/media_accounts.soql), and [`scripts/salesforce/soql/account.soql`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/scripts/salesforce/soql/account.soql).
- **Dashboard UI Enhancements for Multi-Object NLP:**
  - Added dynamic `renderNlpPromptChips(sobject)` in [`src/dashboard-ui/app.js`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/src/dashboard-ui/app.js) generating tailored prompt chips when switching between Account, Contact, Opportunity, and Lead.
  - Configured automatic entity switching in the UI selector when an NLP query targets a different sObject.
  - Enhanced table row rendering with customized details per object (Title/Email/Phone for Contacts, StageName/Amount/Probability for Opportunities, Status/Company for Leads) and colored status badges (`Media`, `Won`, `Qualified`).
  - Connected the Query Inspector modal to display live compiled SOQL, openCypher, and human-readable NLP interpretation summaries.
