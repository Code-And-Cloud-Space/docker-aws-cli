# Salesforce (Live) <-> AWS Integration Platform (OAuth 2.0 Auth Code & MySQL)

A complete local Docker environment replicating an end-to-end integration between **Live Salesforce** (via **OAuth 2.0 Authorization Code Flow**) and **AWS Cloud Services** (LocalStack S3, DynamoDB, SQS, Secrets Manager) with **MySQL 8.0 Multi-User Token Expiration Management** and a **Vercel CLI-powered** Web UI Dashboard.

---

## 🌟 Architecture & Features
- **OAuth 2.0 Web Server / Authorization Code Flow:** Full OAuth consent and callback lifecycle (`/api/auth/salesforce/callback`).
- **AWS Secrets Manager Replication:** Refresh tokens and client secrets are securely stored as encrypted secrets in AWS Secrets Manager, never as plain text in the database.
- **MySQL Multi-User Token Expiry Engine:** `users` and `salesforce_oauth_tokens` tables track exact expiration timestamps (`expires_at`), enabling each user to connect their own Salesforce Org independently with automatic token refresh on expiry.
- **Modular Monorepo Structure (`src/`):** Clean separation of backend (`src/integration-engine`), frontend (`src/dashboard-ui`), and scripts (`src/scripts`).
- **Local AWS Cloud (LocalStack):** S3 (`salesforce-raw-events`, `salesforce-backups`), DynamoDB (`SalesforceSyncRecords`), SQS (`salesforce-inbound-queue`, `salesforce-deadletter-queue`), and Secrets Manager.
- **Web UI Management Dashboard (Port 3000):** Vercel CLI-powered interface with multi-user switcher, real-time token expiry countdown timer, one-click OAuth login, and Secrets Manager inspector.

---

## 📂 Project Structure

```
.
├── src/                                    # 📁 Development Modules
│   ├── integration-engine/                 # FastAPI Middleware Backend
│   │   ├── app/
│   │   │   ├── main.py                     # API Routes & Webhooks
│   │   │   ├── config.py                   # Environment & Database Config
│   │   │   ├── database.py                 # MySQL SQLAlchemy Models (users, tokens)
│   │   │   ├── oauth_service.py            # OAuth 2.0 Auth Code & Token Refresh Engine
│   │   │   ├── secrets_manager.py          # AWS Secrets Manager Replicator
│   │   │   ├── salesforce_client.py        # User-Scoped SOQL & REST Client
│   │   │   ├── aws_client.py               # Boto3 S3 / DynamoDB / SQS
│   │   │   └── sync_service.py             # Event Sync Pipelines
│   │   └── Dockerfile
│   ├── dashboard-ui/                       # Vercel CLI Frontend
│   │   ├── index.html, app.js, vercel.json, package.json, Dockerfile
│   └── scripts/                            # Provisioning Scripts (init-mysql.sql, init-aws.sh)
├── docs/                                   # 📖 Documentation Hub (ADRs, Work Progress)
├── .agents/                                # 🛡️ Always-on AI Rules & Safeguards
├── .venv/                                  # Local Python Virtual Environment
├── docker-compose.yml                      # LocalStack + MySQL + FastAPI + Vercel CLI
├── .env & .env.example                     # Salesforce OAuth & DB Credentials
└── README.md
```

---

## ⚡ Quick Start

### 1. Configure Salesforce Connected App Callback URL
Set the Callback URL in your Salesforce Connected App to:
```
http://localhost:8000/api/auth/salesforce/callback
```

### 2. Configure [.env](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/.env)
```env
SALESFORCE_CLIENT_ID=your_consumer_key
SALESFORCE_CLIENT_SECRET=your_consumer_secret
```

### 3. Start Containers
```bash
docker compose up -d --build
```

### 4. Open the Web Dashboard
Visit **[http://localhost:3000](http://localhost:3000)**, select a user, and click **"Connect Live Salesforce"**!
