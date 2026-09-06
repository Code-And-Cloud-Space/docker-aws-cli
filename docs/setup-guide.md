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
- **Dashboard Web UI:** `http://localhost:3000` (Modern dark-themed UI with glassmorphic Toast notifications, live countdown timers & multi-tab CRM/AWS explorers)
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

### 6. Direct AWS CLI via LocalStack Container
```bash
docker compose exec aws-cli aws --endpoint-url=http://localstack:4566 s3 ls s3://salesforce-raw-events --recursive
docker compose exec aws-cli aws --endpoint-url=http://localstack:4566 dynamodb scan --table-name SalesforceSyncRecords
```

