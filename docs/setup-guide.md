# Setup & Operations Guide

This guide provides instructions to run, configure, test, and troubleshoot the **Salesforce (Live) <-> AWS Integration Platform**.

---

## ⚡ Quick Start

```bash
# 1. Start all 5 Docker containers
docker compose up -d

# 2. Check service health & status
curl http://localhost:8000/api/status

# 3. Open Web UI Dashboard
open http://localhost:3000
```

---

## 🌐 Complete Platform URLs & Endpoint Catalog

### 1. Web Applications & Interactive Portals
- **Dashboard Web UI:** `http://localhost:3000` (Modern dark-themed UI with glassmorphic Toast notifications, live countdown timers, direct Salesforce record ID hyperlinks & multi-tab CRM/AWS explorers)
- **Interactive Swagger API Docs:** `http://localhost:8000/docs`
- **ReDoc API Documentation:** `http://localhost:8000/redoc`
- **OpenAPI JSON Schema:** `http://localhost:8000/openapi.json`
- **LocalStack AWS Health:** `http://localhost:4566/_localstack/health`

### 2. Core System & OAuth Endpoints (`http://localhost:8000`)
- `GET /` - Root health check & engine metadata
- `GET /api/status` - System health, AWS status & active Salesforce session details (supports `X-Session-ID`)
- `GET /api/auth/salesforce/login` - Generates Salesforce OAuth 2.0 PKCE (S256) authorization URL
- `GET /api/auth/salesforce/callback` - OAuth redirect handler (exchanges code & verifier for tokens)
- `POST /api/auth/salesforce/refresh` - Rotates tokens via AWS Secrets Manager for active session
- `POST /api/auth/salesforce/disconnect` - Revokes session token & removes Secrets Manager entry

### 3. Live Salesforce CRM Data Endpoints
- `GET /api/salesforce/records/Account` - Query live Salesforce Account sObjects
- `GET /api/salesforce/records/Contact` - Query live Salesforce Contact sObjects
- `GET /api/salesforce/records/Opportunity` - Query live Salesforce Opportunity sObjects
- `GET /api/salesforce/records/Lead` - Query live Salesforce Lead sObjects
- `POST /api/salesforce/records/{sobject}` - Create record in Live Salesforce & auto-mirror to DB + AWS

### 4. Multi-Target Sync Pipelines
- `POST /api/sync/record` - Single record sync to MySQL (`salesforce_accounts`/`contacts`/`opportunities`), DynamoDB (`SalesforceSyncRecords`), and S3 (`salesforce-raw-events`)
- `POST /api/sync/salesforce-to-aws` - Full batch sync pipeline
- `POST /api/sync/aws-to-salesforce` - Upsert record into Live Salesforce from AWS
- `POST /api/webhook/salesforce-cdc` - Webhook ingestion for Change Data Capture events

### 5. MySQL Relational CRM DB Explorers
- `GET /api/db/accounts` - Fetch synced accounts from MySQL
- `GET /api/db/contacts` - Fetch synced contacts from MySQL
- `GET /api/db/opportunities` - Fetch synced opportunities from MySQL

### 6. AWS / LocalStack Resource Explorers
- `GET /api/aws/dynamodb/records` - Scan DynamoDB table `SalesforceSyncRecords`
- `GET /api/aws/s3/files` - List archived objects in S3 bucket `salesforce-raw-events`
- `GET /api/aws/sqs/stats` - Inspect queue metrics for `salesforce-inbound-queue` and DLQ
- `GET /api/secrets` - Inspect AWS Secrets Manager stored secret metadata
- `GET /api/logs` - Integration audit & stream event logs

### 7. Admin Custom Field Mapping & Dynamic MySQL Schema Studio Endpoints
- `GET /api/salesforce/describe/{sobject}` - Fetch live sObject field schema & data types
- `POST /api/salesforce/custom-query` - Dynamic SOQL execution with field mappings, filters, sorting & limits
- `GET /api/admin/mappings` - List saved custom mapping profiles
- `POST /api/admin/mappings` - Save new custom mapping profile
- `PUT /api/admin/mappings/{id}` - Update existing mapping profile
- `DELETE /api/admin/mappings/{id}` - Delete mapping profile
- `GET /api/db/schema-for-sobject/{sobject}` - Inspect target MySQL table schema and columns for mapping
- `POST /api/db/add-column` - Dynamically alter MySQL table to add new column on-demand

---

## 🐳 Running Containers & Ports

| Container Service | Internal Port | Host Port | Purpose | Live Volume Mount (Hot-Reload) |
| :--- | :--- | :--- | :--- | :--- |
| `integration-sync-engine` | `8000` | `8000` | FastAPI Engine, OAuth Middleware, Sync Pipeline | `./src/integration-engine/app:/app/app` (`--reload`) |
| `integration-dashboard-ui` | `3000` | `3000` | Vercel Serve Frontend Web Dashboard | `./src/dashboard-ui:/app` |
| `salesforce-mysql-db` | `3306` | `3307` | Relational DB (`salesforce_accounts`, `contacts`, `opportunities`) | `mysql_data:/var/lib/mysql` |
| `localstack-aws` | `4566` | `4566` | LocalStack AWS (S3, DynamoDB, SQS, Secrets Manager) | `./.localstack:/var/lib/localstack` |
| `aws-cli-runner` | N/A | N/A | AWS CLI runner container | N/A |

> [!TIP]
> **Live Development Active:** Any code changes in `src/integration-engine/app/` automatically trigger Uvicorn hot-reloads inside Docker without restarting the container. Any edits in `src/dashboard-ui/` (`index.html`, `app.js`, styles) immediately reflect upon browser refresh.

---

## 🔑 Environment Configuration (`.env`)

```ini
# Salesforce Live Org OAuth Credentials
SALESFORCE_AUTH_URL=https://login.salesforce.com/services/oauth2/authorize
SALESFORCE_TOKEN_URL=https://login.salesforce.com/services/oauth2/token
SALESFORCE_CLIENT_ID=your_connected_app_consumer_key
SALESFORCE_CLIENT_SECRET=your_connected_app_consumer_secret
SALESFORCE_REDIRECT_URI=http://localhost:8000/api/auth/salesforce/callback
SALESFORCE_SCOPES=api refresh_token offline_access

# AWS / LocalStack Configuration
AWS_REGION=us-east-1
AWS_ENDPOINT_URL=http://localstack:4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test

# MySQL Database Configuration
MYSQL_HOST=mysql-db
MYSQL_PORT=3306
MYSQL_HOST_PORT=3307
MYSQL_DATABASE=salesforce_integration
MYSQL_USER=sf_user
MYSQL_PASSWORD=sf_password
MYSQL_ROOT_PASSWORD=root_password
```

---

## 🛠️ Testing Commands

### 1. Check Session Status (Isolated vs Authenticated)
```bash
# Unauthenticated / Incognito session (returns disconnected)
curl -s http://localhost:8000/api/status | jq .

# Authenticated session
curl -s http://localhost:8000/api/status -H "X-Session-ID: <your_session_id>" | jq .
```

### 2. Fetch Live Salesforce Records (Protected by Session)
```bash
# Unauthenticated request -> returns 401 Unauthorized
curl -s -w "\nHTTP_STATUS:%{http_code}\n" http://localhost:8000/api/salesforce/records/Account

# Authenticated request -> returns 200 with live records
curl -s http://localhost:8000/api/salesforce/records/Account -H "X-Session-ID: <your_session_id>" | jq .
```

### 3. Sync Single Record to MySQL, DynamoDB & S3
```bash
curl -s -X POST http://localhost:8000/api/sync/record \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: <your_session_id>" \
  -d '{"sobject": "Account", "record_id": "0015j00000BelpsAAB"}' | jq .
```

### 4. Inspect Local MySQL Tables (Protected by Session)
```bash
# Unauthenticated request -> returns 401 Unauthorized
curl -s -i http://localhost:8000/api/db/accounts

# Authenticated request -> returns 200 with synced records
curl -s http://localhost:8000/api/db/accounts -H "X-Session-ID: <your_session_id>" | jq .
curl -s http://localhost:8000/api/db/contacts -H "X-Session-ID: <your_session_id>" | jq .
curl -s http://localhost:8000/api/db/opportunities -H "X-Session-ID: <your_session_id>" | jq .
```

### 5. Inspect AWS / LocalStack Resources (Protected by Session)
```bash
# Unauthenticated request -> returns 401 Unauthorized
curl -s -i http://localhost:8000/api/aws/dynamodb/records
curl -s -i http://localhost:8000/api/aws/s3/files

# Authenticated request -> returns 200 with resources
curl -s http://localhost:8000/api/aws/dynamodb/records -H "X-Session-ID: <your_session_id>" | jq .
curl -s http://localhost:8000/api/aws/s3/files -H "X-Session-ID: <your_session_id>" | jq .
curl -s http://localhost:8000/api/aws/s3/file?key=2026/09/05/created-Account-001.json -H "X-Session-ID: <your_session_id>" | jq .
```

### 6. Admin Studio: Inspect Schema & Add Dynamic MySQL Column
```bash
# 1. Inspect MySQL columns for an sObject
curl -s http://localhost:8000/api/db/schema-for-sobject/Account -H "X-Session-ID: <your_session_id>" | jq .

# 2. Add a new column dynamically to MySQL table
curl -s -X POST http://localhost:8000/api/db/add-column \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: <your_session_id>" \
  -d '{"sobject": "Account", "column_name": "lead_score", "data_type": "INT"}' | jq .
```

### 7. Direct AWS CLI via LocalStack Container
```bash
docker compose exec aws-cli aws --endpoint-url=http://localstack:4566 s3 ls s3://salesforce-raw-events --recursive
docker compose exec aws-cli aws --endpoint-url=http://localstack:4566 dynamodb scan --table-name SalesforceSyncRecords
```

---

## 🔧 Troubleshooting Guide


### Issue: `OAUTH_EC_APP_NOT_FOUND` ("External client app is not installed in this org")

#### Why this happens:
1. **Logged into the Wrong Salesforce Org / Account**: Your browser logged in with a Salesforce user/organization different from the one where the External Client App was created (e.g. Trailhead Playground A vs Playground B, or personal org vs work org). Unlike legacy Connected Apps, an External Client App created in Org A is not accessible in Org B unless installed as a managed package.
2. **Login URL / Org Domain Mismatch (`SALESFORCE_LOGIN_URL`)**: `SALESFORCE_LOGIN_URL` is set to `https://login.salesforce.com` (Production), but your app was created in a **Sandbox** (requires `https://test.salesforce.com`) or custom **My Domain** (e.g. `https://yourcompany.my.salesforce.com`). When hitting the login URL, Salesforce searches the wrong org ecosystem.
3. **Distribution State set to "Packaged" instead of "Local"**: In Salesforce Setup -> **External Client App Manager**, if the Distribution State is `Packaged`, Salesforce requires it to be deployed and installed via package. In the local developer org, it must be `Local`.
4. **App Not Authorized / Policies Restricted**: In **Manage External Client Apps**, under **OAuth Policies**, "Permitted Users" is restricted to "Admin approved users are pre-authorized" and your user profile or permission set has not been granted access.
5. **Propagation Delay**: Salesforce takes up to 5–10 minutes to replicate External Client App OAuth metadata after creation or updates.

#### How to resolve:
1. **Ensure You Log In to the Exact Org Where the App Was Created**:
   - Log out of all Salesforce accounts in your browser (or use an Incognito / Private window).
   - Verify the login email belongs specifically to the Salesforce Org where you set up the External Client App.
2. **Match Login Domain in `.env`**:
   - If using a Sandbox: set `SALESFORCE_LOGIN_URL=https://test.salesforce.com`
   - If using a My Domain URL: set `SALESFORCE_LOGIN_URL=https://<your-domain>.my.salesforce.com`
3. **Verify App Distribution State**:
   - Go to **Setup** -> **Apps** -> **External Client Apps** -> **External Client App Manager**.
   - Find your app -> Ensure **Distribution State** is **Local**.
4. **Check OAuth Policies**:
   - In Setup, search **Manage External Client Apps** -> Select your app -> **Edit Policies**.
   - Under **OAuth Policies**, set **Permitted Users** to *"All users may self-authorize"*.
5. **Verify the Consumer Key**:
   - In **External Client App Manager** -> **OAuth Settings** -> **Consumer Details**, copy the **Consumer Key** and verify it matches `SALESFORCE_CLIENT_ID` in `.env`.

### Issue: "Refresh Failed: No refresh token found in Secrets Manager. Please re-authenticate."

#### Why this happens:
1. **LocalStack / Secrets Manager Reset**: LocalStack container was restarted or ephemeral storage was cleared while the MySQL database retained an existing session record with an expired access token.
2. **Missing OAuth Scope in Connected App**: The Salesforce Connected App was created without the `refresh_token, offline_access` OAuth scope, or the scope was not requested during login. Consequently, Salesforce only issued a short-lived `access_token` and no `refresh_token`.

#### How to resolve:
1. **Quick Re-Authentication**:
   - Open the Dashboard at [http://localhost:3000](http://localhost:3000).
   - Click the **Connect Salesforce** button in the top navigation or status card.
   - Complete the Salesforce login prompt to generate a new `access_token` and `refresh_token`.
2. **Verify Connected App Scopes in Salesforce**:
   - In Salesforce Setup, navigate to **App Manager** -> Locate your Connected App -> **Edit / Manage**.
   - Under **Selected OAuth Scopes**, ensure **"Perform requests at any time (refresh_token, offline_access)"** and **"Manage user data via APIs (api)"** are selected.
   - Under **OAuth Policies**, ensure the **Refresh Token Policy** is set to *"Refresh token is valid until revoked"*.

---

## ⚡ Salesforce CLI (`sf` / `sfdx`) Operations Runbook

The repository is configured with a standard Salesforce DX source structure (`force-app`) and [`sfdx-project.json`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/sfdx-project.json).

### 1. Authorize an Org
```bash
# Authorize Developer Edition or Production Org
sf org login web --set-default --alias my-dev-org

# Authorize Sandbox Org
sf org login web --instance-url https://test.salesforce.com --alias my-sandbox-org
```

### 2. Deploy & Retrieve Source (`force-app`)
```bash
# Deploy all source from force-app to default org
sf project deploy start --source-dir force-app

# Retrieve source from org into force-app using manifest
sf project retrieve start --manifest manifest/package.xml

# Retrieve specific metadata (e.g. ApexClass)
sf project retrieve start --metadata ApexClass:AccountController
```

### 3. Run Ad-Hoc Scripts & Queries
```bash
# Execute anonymous Apex
sf apex run --file scripts/salesforce/apex/hello.apex

# Execute SOQL query against connected org
sf data query --file scripts/salesforce/soql/account.soql
sf data query --file scripts/salesforce/soql/media_accounts.soql

# Execute Media Account Search via Integration Engine API
curl -s -H "X-Session-ID: <session_id>" "http://localhost:8000/api/salesforce/records/Account?media_only=true"

# Execute Multi-Object NLP Natural Language Queries via Integration Engine API
# 1. Account Search
curl -s -X POST "http://localhost:8000/api/salesforce/nlp-query" \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: <session_id>" \
  -d '{"query": "Search All Media Type of Account", "limit": 50}'

# 2. Contact Search (with Account Relationship Resolution)
curl -s -X POST "http://localhost:8000/api/salesforce/nlp-query" \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: <session_id>" \
  -d '{"query": "Get Global Media person", "limit": 50}'

# 3. Opportunity Search
curl -s -X POST "http://localhost:8000/api/salesforce/nlp-query" \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: <session_id>" \
  -d '{"query": "Closed Won deals > 50000", "limit": 50}'

# 4. Lead Search
curl -s -X POST "http://localhost:8000/api/salesforce/nlp-query" \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: <session_id>" \
  -d '{"query": "Qualified leads in Media", "limit": 50}'
```

---

## 🎬 Testing Multi-Object NLP & Internal Local LLM in UI

1. Open the UI at `http://localhost:3000`.
2. Connect your Live Salesforce Org using **"Connect Live Salesforce"**.
3. In the **Live Salesforce sObject Explorer** tab:
   - **Account NLP Queries:**
     - Select **Accounts** in the dropdown.
     - Click **"Search All Media Type of Account"** or click chips like `"Get all accounts with media type"` or `"High revenue accounts ($1M+)"`.
     - Displays Media accounts with purple badges (`Media`) and revenue details.
   - **Contact NLP Queries (with Parent Account & Cross-Field Media Resolution):**
     - Select **Contacts** or click `"Get Global Media person"` or `"media related person"`.
     - When clicking `"media related person"`:
       - The engine executes cross-field evaluation: `Account.Name LIKE '%Media%' OR Account.Type = 'Media' OR Account.Industry = 'Media' OR Title LIKE '%Media%' OR FirstName LIKE '%Media%' OR LastName LIKE '%Media%' OR Email LIKE '%media%'`.
       - Matches all contacts with media in their name, title, or parent company (e.g. Vikas Kumar Tank @ ABP News, Jon Amos @ Global Media).
     - When clicking `"Get Global Media person"`:
       - Matches contacts where `Account.Name = 'Global Media'`.
       - Displays `Acct: <Account.Name>` in purple bold text in each contact row.
   - **Opportunity NLP Queries:**
     - Select **Opportunities** or click `"Opportunity of Media"`.
     - When clicking `"Opportunity of Media"`:
       - The engine evaluates parent accounts (`Account.Name LIKE '%Media%' OR Account.Type = 'Media' OR Account.Industry = 'Media'`) and opportunity titles (`Name LIKE '%Media%'`).
       - Loads matching opportunities (e.g., `salesforce.com - 5000 Widgets`, `salesforce.com - 500 Widgets`, `Global Media - 400 Widgets`).
     - Or click `"Closed Won opportunities"` to view won deals.

---

## 🧪 Testing the Decoupled Standalone LLM Engine (`src/llm_engine`)

You can execute the internal neural LLM engine and full verification suite directly from the command line inside the Python virtual environment (`.venv`):

```bash
# 1. Activate project virtual environment
source .venv/bin/activate

# 2. Run standalone LLM benchmark suite (100% in-process, < 1ms)
PYTHONPATH=src python3 src/llm_engine/benchmark.py
```

### Direct Python Invocation:
```bash
python3 -c "
import sys
sys.path.insert(0, 'src')
from llm_engine import internal_llm

queries = [
    'open pipeline',
    'open deals',
    'active account',
    'company',
    'Search All Media Type of Account',
    'Get Global Media person',
    'media related person',
    'Opportunity of Media',
    'open lead',
    'Closed Won deals > 50000',
    'Qualified leads in Media'
]

for q in queries:
    res = internal_llm.generate_query(q)
    print(f'=== Query: {q} ===')
    print(f'Target:  {res["sobject"]}')
    print(f'SOQL:    {res["soql"]}')
    print(f'Cypher:  {res["cypher"]}')
    print(f'Latency: {res["llm_telemetry"]["inference_time_ms"]} ms | Confidence: {res["llm_telemetry"]["confidence_score"]}')
    print()
"
```

### Inspect or Test Autonomous Web Learner
```bash
python3 -c "
import sys
sys.path.insert(0, 'src')
from llm_engine import internal_llm, crm_dictionary

# Query an unknown term to trigger web learning & persistence
res = internal_llm.generate_query('show all agencies')
print('Learned entries in dictionary:', list(crm_dictionary.data.get('learned_terms', {}).keys()))
"
```






