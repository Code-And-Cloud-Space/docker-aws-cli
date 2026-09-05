# Live Salesforce & AWS Docker Setup Guide

This guide walks through connecting your **Live Salesforce Org** (Developer Org, Sandbox, or Production) to local AWS services running in Docker, as well as setting up your local Python virtual environment.

---

## 🐍 Python Virtual Environment Setup (`.venv`)

For local development, IDE auto-completion, linting, and running integration scripts without Docker:

```bash
# 1. Activate the created virtual environment:
source .venv/bin/activate

# 2. Run local tests / linting:
pytest
black . --check
```

---

## 🔑 Step 1: Configure Live Salesforce Credentials

### Option A: Using Salesforce Connected App + Username/Password (Recommended)
1. In your Salesforce Org, go to **Setup ➔ App Manager ➔ New Connected App**.
2. Set:
   - **Connected App Name:** `AWS_Docker_Integration`
   - **API (Enable OAuth Settings):** Checked
   - **Callback URL:** `http://localhost:8000/callback` (or `https://login.salesforce.com/services/oauth2/success`)
   - **Selected OAuth Scopes:** `Manage user data via APIs (api)`, `Perform requests at any time (refresh_token, offline_access)`
3. Save the Connected App and copy:
   - **Consumer Key** (`SALESFORCE_CLIENT_ID`)
   - **Consumer Secret** (`SALESFORCE_CLIENT_SECRET`)
4. In your `.env` file, configure:
   ```env
   SALESFORCE_AUTH_TYPE=oauth_password
   SALESFORCE_LOGIN_URL=https://login.salesforce.com   # or https://test.salesforce.com for Sandboxes
   SALESFORCE_USERNAME=your_salesforce_username@domain.com
   SALESFORCE_PASSWORD=your_salesforce_password
   SALESFORCE_SECURITY_TOKEN=your_security_token       # Reset under: Settings -> Reset My Security Token
   SALESFORCE_CLIENT_ID=your_consumer_key
   SALESFORCE_CLIENT_SECRET=your_consumer_secret
   ```

### Option B: Using Direct Access Token (Quick Test)
If you already have a temporary Access Token or Session ID (e.g. from SFDX CLI `sf org display`):
```env
SALESFORCE_AUTH_TYPE=access_token
SALESFORCE_INSTANCE_URL=https://your-domain.my.salesforce.com
SALESFORCE_ACCESS_TOKEN=00D5g00000...
```

---

## 🚀 Step 2: Start the Dockerized Platform

```bash
docker compose up -d --build
```

View the logs:
```bash
docker compose logs -f integration-engine
```

---

## 🖥️ Step 3: Access the Management UI Dashboard

Open your browser at **[http://localhost:3000](http://localhost:3000)**.

- **Salesforce Explorer Tab:** View real-time sObjects directly from your Live Salesforce Org (Accounts, Contacts, Opportunities, Leads).
- **AWS DynamoDB Tab:** Inspect synchronized records in `SalesforceSyncRecords`.
- **AWS S3 Archive Tab:** View JSON snapshots in `salesforce-raw-events`.
- **AWS SQS Tab:** Monitor the message queue pipeline.
- **Sync & Event Actions:** Trigger full live synchronization or push synthetic events into Salesforce.

---

## 🧪 Step 4: Test Live Syncing

1. **Trigger Full Sync from Live Salesforce to AWS:**
   Click **"Execute Full Sync Pipeline"** in the UI or run:
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
