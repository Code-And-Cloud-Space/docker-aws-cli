# System Architecture & Integration Patterns

This document details the architecture, data models, integration flows, and Docker topology for the Live Salesforce <-> AWS Integration Platform.

---

## 🏗️ Architecture Topology

```
┌────────────────────────────────────────┐
│     Live Salesforce Org (Cloud)        │
│ (https://login.salesforce.com or MyOrg)│
└──────────────────┬─────────────────────┘
                   │ HTTPS REST / SOQL / OAuth
                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         Docker Compose Network                         │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │           Integration Engine (FastAPI Middleware)              │   │
│   │                     (Port 8000)                                │   │
│   └───────────────┬───────────────────────────────┬────────────────┘   │
│                   │                               │                    │
│                   ▼                               ▼                    │
│   ┌───────────────────────────────┐   ┌────────────────────────────┐   │
│   │       Web UI Dashboard        │   │    AWS LocalStack (Cloud)  │   │
│   │         (Port 3000)           │   │         (Port 4566)        │   │
│   └───────────────────────────────┘   └─────────────┬──────────────┘   │
│                                                     │                  │
│                                 ┌───────────────────┼──────────────┐   │
│                                 ▼                   ▼              ▼   │
│                            ┌─────────┐        ┌───────────┐    ┌───────┐
│                            │ AWS S3  │        │ DynamoDB  │    │AWS SQS│
│                            └─────────┘        └───────────┘    └───────┘
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Core Integration Flows

### Flow 1: Live Salesforce Data Query & Ingestion -> AWS
1. **Trigger:** Manual trigger via UI / API or scheduled worker.
2. **Data Extraction:** The Integration Engine performs SOQL queries against Live Salesforce (`Account`, `Contact`, `Opportunity`, `Lead`).
3. **Queue Processing:** Extracted events are enqueued into AWS SQS (`salesforce-inbound-queue`).
4. **Storage & Indexing:**
   - Mirrored records are indexed into **AWS DynamoDB** (`SalesforceSyncRecords`).
   - Raw JSON payloads are archived into **AWS S3** bucket `salesforce-raw-events/YYYY/MM/DD/<id>.json`.
5. **Observability:** Event records appear live on the Web UI.

### Flow 2: AWS Event / Ingestion -> Live Salesforce Push
1. **Trigger:** Event from upstream AWS service or UI manual trigger.
2. **Transformation:** Integration Engine maps payload to standard Salesforce schema.
3. **Upsert to Salesforce:** Integration Engine calls Salesforce REST API (`/services/data/v58.0/sobjects/<sObject>`) to create or update live CRM records.
4. **Audit Log:** Synchronized state is committed to DynamoDB and the audit log.

---

## 📦 Docker Container Services

| Service Name | Container / Image | Port | Purpose |
| :--- | :--- | :--- | :--- |
| **`localstack`** | `localstack/localstack:latest` | `4566` | Emulates AWS Cloud APIs (S3, DynamoDB, SQS, SNS) |
| **`integration-engine`** | Python / FastAPI + Boto3 | `8000` | Sync middleware connecting Live Salesforce to AWS |
| **`dashboard-ui`** | Nginx / Alpine | `3000` | Local visual management dashboard |
| **`aws-cli`** | `amazon/aws-cli` | - | Helper container for initializing AWS resources & ad-hoc CLI tasks |

---

## 🗄️ AWS Resource Definitions

### 1. S3 Buckets
- `salesforce-raw-events`: Stores raw JSON event payloads from Salesforce.
- `salesforce-backups`: Nightly or on-demand sObject JSON dumps.

### 2. DynamoDB Tables
- **Table Name:** `SalesforceSyncRecords`
  - **Partition Key:** `sObjectType` (String)
  - **Sort Key:** `salesforceId` (String)
  - **Attributes:** `awsSyncStatus`, `syncedAt`, `payload`

### 3. SQS Queues
- `salesforce-inbound-queue`: Primary ingestion queue.
- `salesforce-deadletter-queue`: DLQ for events that failed processing after retries.
