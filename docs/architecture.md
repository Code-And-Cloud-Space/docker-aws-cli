# System Architecture & Integration Patterns

This document details the architecture, data models, integration flows, and Docker topology for the Live Salesforce <-> AWS Integration Platform.

---

## 🏗️ Modular Architecture Topology (`src/`)

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
│   │     src/integration-engine (FastAPI Middleware Backend)        │   │
│   │                     (Port 8000)                                │   │
│   └───────────────┬───────────────────────────────┬────────────────┘   │
│                   │                               │                    │
│                   ▼                               ▼                    │
│   ┌───────────────────────────────┐   ┌────────────────────────────┐   │
│   │       src/dashboard-ui        │   │    AWS LocalStack (Cloud)  │   │
│   │       (Vercel CLI @ 3000)     │   │         (Port 4566)        │   │
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

## 📂 Source Code Structure (`src/`)

```
src/
├── integration-engine/        # Python FastAPI Integration Middleware
│   ├── app/
│   │   ├── main.py            # API routes & UI proxies
│   │   ├── config.py          # Environment settings
│   │   ├── aws_client.py      # Boto3 S3/DynamoDB/SQS client
│   │   ├── salesforce_client.py # Live Salesforce OAuth/SOQL client
│   │   └── sync_service.py    # Pipeline logic & event audit
│   ├── Dockerfile
│   └── requirements.txt
│
├── dashboard-ui/              # Frontend Dashboard Module
│   ├── index.html             # Visual explorer interface
│   ├── app.js                 # Live reactive state & API integration
│   ├── package.json           # Node / Vercel CLI runner
│   ├── vercel.json            # Vercel configuration
│   └── Dockerfile             # Node 20 + Vercel CLI container
│
└── scripts/                   # Infrastructure Provisioning Module
    └── init-aws.sh            # Auto-creates S3 buckets, DynamoDB, SQS
```

---

## 📦 Docker Container Services

| Service Name | Source Module | Port | Runtime | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **`localstack`** | `localstack/localstack` | `4566` | LocalStack | Emulates AWS Cloud APIs (S3, DynamoDB, SQS) |
| **`integration-engine`** | `src/integration-engine` | `8000` | Python 3.11 / FastAPI | Sync middleware connecting Live Salesforce to AWS |
| **`dashboard-ui`** | `src/dashboard-ui` | `3000` | Node 20 / Vercel CLI | Local visual management dashboard |
| **`aws-cli`** | `amazon/aws-cli` | - | AWS CLI | Helper container for initializing AWS resources |
