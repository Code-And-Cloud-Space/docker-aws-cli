# Salesforce (Live) <-> AWS Integration Platform (Docker Dev Replica)

A complete local Docker environment replicating an end-to-end integration between **Live Salesforce** and **AWS Cloud Services** (LocalStack S3, DynamoDB, SQS) with a **Vercel CLI-powered** Web UI Dashboard.

---

## 🌟 Architecture & Features
- **Centralized `src/` Module Hierarchy:** All development code is organized into sub-modules under `src/`.
- **Live Salesforce CRM Connectivity:** Direct OAuth 2.0 integration and live SOQL query execution for standard and custom sObjects.
- **Local AWS Cloud (LocalStack):** S3 (`salesforce-raw-events`, `salesforce-backups`), DynamoDB (`SalesforceSyncRecords`), and SQS (`salesforce-inbound-queue`, `salesforce-deadletter-queue`).
- **Integration Sync Middleware (`src/integration-engine`):** FastAPI engine handling bi-directional sync, SQS messaging, DynamoDB indexing, and audit logging.
- **Web UI Management Dashboard (`src/dashboard-ui`):** Modern UI served via **Vercel CLI** (`vercel dev` on port 3000).

---

## 📂 Project Structure

```
.
├── src/                          # 📁 All Development Modules
│   ├── integration-engine/       # FastAPI Middleware Backend
│   ├── dashboard-ui/             # Vercel CLI Frontend
│   └── scripts/                  # AWS LocalStack Init Scripts
├── docs/                         # 📖 Documentation Hub
│   ├── work-progress.md
│   ├── discussions-and-decisions.md
│   ├── architecture.md
│   └── setup-guide.md
├── .agents/                      # 🛡️ Always-on Agent Rules & Safeguards
│   └── rules/mandatory-documentation-safeguard.md
├── .venv/                        # Local Python Virtual Environment
├── docker-compose.yml            # Docker Topology Orchestrator
├── requirements.txt              # Root Python Dependencies
├── AGENTS.md & GEMINI.md         # Pair-Programming Directives
├── .env & .env.example           # Live Credentials & Config
└── README.md
```

---

## ⚡ Quick Start

### 1. Configure Live Salesforce Credentials
Edit [.env](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/.env):
```env
SALESFORCE_AUTH_TYPE=oauth_password
SALESFORCE_LOGIN_URL=https://login.salesforce.com
SALESFORCE_USERNAME=your_username@domain.com
SALESFORCE_PASSWORD=your_password
SALESFORCE_SECURITY_TOKEN=your_security_token
SALESFORCE_CLIENT_ID=your_connected_app_consumer_key
SALESFORCE_CLIENT_SECRET=your_connected_app_consumer_secret
```

### 2. Start Containers
```bash
docker compose up -d --build
```

### 3. Open the Web Dashboard (Vercel CLI)
Visit **[http://localhost:3000](http://localhost:3000)** in your browser.

---

## 🔗 Ports & Endpoints

| Service | Endpoint | Runtime | Description |
| :--- | :--- | :--- | :--- |
| **Web UI Dashboard** | [http://localhost:3000](http://localhost:3000) | Vercel CLI | Live visual CRM & AWS explorer |
| **Integration Engine API** | [http://localhost:8000/docs](http://localhost:8000/docs) | FastAPI | Interactive Swagger API docs |
| **LocalStack AWS Gateway** | [http://localhost:4566](http://localhost:4566) | LocalStack | Local S3, DynamoDB, and SQS endpoint |
