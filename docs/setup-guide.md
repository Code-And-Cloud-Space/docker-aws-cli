# Live Salesforce & AWS Docker Setup Guide

This guide walks through connecting your **Live Salesforce Org** (Developer Org, Sandbox, or Production) to local AWS services running in Docker, using the **`src/` modular codebase** and the **Vercel CLI** dashboard.

---

## 🏗️ Project Module Layout (`src/`)

All active development code is centralized under the `src/` directory:
- `src/integration-engine/`: Python FastAPI backend.
- `src/dashboard-ui/`: Frontend UI running on Vercel CLI.
- `src/scripts/`: LocalStack initialization scripts.

---

## 🐍 Python Virtual Environment Setup (`.venv`)

```bash
# 1. Activate the created virtual environment:
source .venv/bin/activate

# 2. Run local tests / linting:
pytest
black . --check
```

---

## 🔑 Step 1: Configure Live Salesforce Credentials

Edit your `.env` file with your Live Salesforce Org details:
```env
SALESFORCE_AUTH_TYPE=oauth_password
SALESFORCE_LOGIN_URL=https://login.salesforce.com   # or https://test.salesforce.com for Sandboxes
SALESFORCE_USERNAME=your_salesforce_username@domain.com
SALESFORCE_PASSWORD=your_salesforce_password
SALESFORCE_SECURITY_TOKEN=your_security_token       # Settings -> Reset My Security Token
SALESFORCE_CLIENT_ID=your_consumer_key
SALESFORCE_CLIENT_SECRET=your_consumer_secret
```

---

## 🚀 Step 2: Start the Dockerized Platform

```bash
docker compose up -d --build
```

View the logs:
```bash
docker compose logs -f integration-engine dashboard-ui
```

---

## 🖥️ Step 3: Access the Management UI Dashboard (Vercel CLI)

Open **[http://localhost:3000](http://localhost:3000)** in your browser. The dashboard is powered by the **Vercel CLI** dev server inside the container.

- **Salesforce Explorer Tab:** View real-time sObjects directly from your Live Salesforce Org.
- **AWS DynamoDB Tab:** Inspect synchronized records in `SalesforceSyncRecords`.
- **AWS S3 Archive Tab:** View JSON snapshots in `salesforce-raw-events`.
- **AWS SQS Tab:** Monitor the message queue pipeline.
- **Sync & Event Actions:** Trigger full live synchronization or push events into Salesforce.

---

## 🧪 Step 4: Test Live Syncing

1. **Trigger Full Sync from Live Salesforce to AWS:**
   ```bash
   curl -X POST http://localhost:8000/api/sync/salesforce-to-aws
   ```

2. **Verify DynamoDB Table Scan:**
   ```bash
   docker compose exec aws-cli aws --endpoint-url=http://localstack:4566 dynamodb scan --table-name SalesforceSyncRecords
   ```

3. **Verify S3 Buckets:**
   ```bash
   docker compose exec aws-cli aws --endpoint-url=http://localstack:4566 s3 ls s3://salesforce-raw-events --recursive
   ```
