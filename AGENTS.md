# Antigravity & AI Agent Guidelines

This repository hosts a Dockerized **Salesforce (Live) <-> AWS Integration Platform** designed for local development and cloud integration.

Follow these instructions when working on this codebase as an AI pair-programmer.

---

## 🧭 Repository Principles & Rules

### 1. Docker-First Development & Live Salesforce
- AWS services run locally inside Docker via `docker compose` with **LocalStack** (`http://localstack:4566`).
- Salesforce connects directly to the user's **Live Salesforce Org** via credentials in `.env`.
- The Web UI Dashboard runs on port `3000`.

### 2. Documentation Hygiene (`docs/` Folder)
- Whenever a new feature, architecture decision, or discussion takes place, **always update the documentation**:
  - Update [docs/work-progress.md](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docs/work-progress.md) for milestone changes and task progress.
  - Record architectural choices or key design decisions in [docs/discussions-and-decisions.md](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docs/discussions-and-decisions.md).
  - Keep [docs/architecture.md](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docs/architecture.md) in sync with data models and container changes.
  - Keep [docs/setup-guide.md](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docs/setup-guide.md) up-to-date with testing commands.

### 3. File Linking & Markdown Format
- In all responses and documentation, use clickable markdown links with the `file://` scheme when referencing repository files (e.g. `[docker-compose.yml](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docker-compose.yml)`).

### 4. Code Standards & Architecture
- **Backend (Integration Engine):** Python 3.11+ / FastAPI, `boto3`, `httpx`, `pydantic`.
- **AWS Services:**
  - S3: Raw payload and backup storage (`salesforce-raw-events`, `salesforce-backups`).
  - DynamoDB: Fast key-value index table `SalesforceSyncRecords`.
  - SQS: `salesforce-inbound-queue` and `salesforce-deadletter-queue`.
- **Frontend (Web UI Dashboard):** Modern responsive dashboard served on port `3000` to inspect both Salesforce live records and AWS resources in real time.

---

## 🛠️ Key CLI Commands

```bash
# Start all containers
docker compose up -d

# View container logs
docker compose logs -f integration-engine

# Run AWS CLI commands against local LocalStack
docker compose exec aws-cli aws --endpoint-url=http://localstack:4566 s3 ls
docker compose exec aws-cli aws --endpoint-url=http://localstack:4566 dynamodb scan --table-name SalesforceSyncRecords

# Rebuild a single service
docker compose up -d --build <service_name>
```
