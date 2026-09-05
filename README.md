# Salesforce (Live) <-> AWS Integration Platform (Docker Dev Replica)

A complete local Docker environment replicating an end-to-end integration between **Live Salesforce** and **AWS Cloud Services** (LocalStack S3, DynamoDB, SQS) with a real-time Web UI Dashboard.

---

## 🌟 Architecture & Features
- **Live Salesforce CRM Connectivity:** Direct OAuth 2.0 integration and live SOQL query execution for standard sObjects (`Account`, `Contact`, `Opportunity`, `Lead`) and custom objects.
- **Local AWS Cloud (LocalStack):** S3 (`salesforce-raw-events`, `salesforce-backups`), DynamoDB (`SalesforceSyncRecords`), and SQS (`salesforce-inbound-queue`, `salesforce-deadletter-queue`).
- **Integration Sync Middleware:** FastAPI engine handling bi-directional data flow, SQS messaging, DynamoDB indexing, and audit logging.
- **Web UI Management Dashboard (Port 3000):** Visual explorer to inspect live Salesforce records, browse DynamoDB records, monitor SQS queues, and trigger synchronization pipelines.

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

### 3. Open the Web Dashboard
Visit **[http://localhost:3000](http://localhost:3000)** in your browser.

---

## 🔗 Ports & Endpoints

| Service | Endpoint | Description |
| :--- | :--- | :--- |
| **Web UI Dashboard** | [http://localhost:3000](http://localhost:3000) | Live visual CRM & AWS explorer |
| **Integration Engine API** | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive Swagger API docs |
| **LocalStack AWS Gateway** | [http://localhost:4566](http://localhost:4566) | Local S3, DynamoDB, and SQS endpoint |

---

## 📚 Documentation & Instructions
- [AGENTS.md](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/AGENTS.md) - Antigravity Agent Guidelines
- [GEMINI.md](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/GEMINI.md) - Agent Rules & Context
- [docs/work-progress.md](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docs/work-progress.md) - Progress & Milestone Tracker
- [docs/discussions-and-decisions.md](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docs/discussions-and-decisions.md) - ADRs & Decisions Log
- [docs/architecture.md](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docs/architecture.md) - System Architecture & Data Flows
- [docs/setup-guide.md](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docs/setup-guide.md) - Step-by-step Setup Guide
