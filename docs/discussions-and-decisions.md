# Project Discussions & Architectural Decision Records (ADRs)

This document captures discussion notes, design requirements, and Architectural Decision Records (ADRs) for the Salesforce-AWS integration project.

---

## 🏛️ Architectural Decision Records (ADRs)

### ADR-001: Local Development First with Docker & LocalStack
- **Date:** 2026-09-05
- **Status:** Accepted
- **Context:**
  Developing and testing cloud integrations directly against live AWS and live Salesforce orgs often leads to slow feedback loops, potential API rate limiting in Developer sandboxes, security/cost risks, and friction for team members without immediate cloud credentials.
- **Decision:**
  Replicate the AWS cloud architecture inside Docker using **LocalStack** (S3, DynamoDB, SQS, SNS), with a local web dashboard on port `3000`.

---

### ADR-002: Event-Driven Asynchronous Integration via SQS & Event Engine
- **Date:** 2026-09-05
- **Status:** Accepted
- **Context:**
  Salesforce updates need to be mirrored or processed in AWS (stored in S3 data lake, indexed in DynamoDB, or processed by downstream workers). Direct synchronous HTTP calls can fail during spikes or downstream outages.
- **Decision:**
  Implement an asynchronous, queue-based architecture:
  - Salesforce changes generate events queued into AWS SQS (`salesforce-inbound-queue`).
  - The Integration Engine consumes SQS messages, commits the state to AWS DynamoDB (for low-latency entity lookups), and archives the raw event snapshot into AWS S3 (`salesforce-raw-events` and `salesforce-backups`).
  - Failed events are redirected to a Dead Letter Queue (`salesforce-deadletter-queue`).

---

### ADR-003: Unified Antigravity & AI Agent Instruction Architecture
- **Date:** 2026-09-05
- **Status:** Accepted
- **Context:**
  The project requires consistent AI pair-programming guidelines, ensuring Antigravity / Gemini / Claude agents follow strict repository rules, documentation hygiene, and Dockerized testing workflows.
- **Decision:**
  Provide root-level `AGENTS.md` and `GEMINI.md` standardizing project principles and file links.

---

### ADR-004: Direct Live Salesforce Org Connectivity from Docker
- **Date:** 2026-09-05
- **Status:** Accepted
- **Context:**
  The developer needs to connect to a **live Salesforce environment** (Developer Org, Sandbox, or Production) even when running the integration and AWS services inside Docker.
- **Decision:**
  - Configured `integration-engine` with multi-mode live Salesforce authentication:
    1. **OAuth 2.0 Username + Password Flow** with security token and Connected App credentials.
    2. **OAuth 2.0 Client Credentials Flow**.
    3. **Pre-authenticated Access Token / Session ID** for instant session testing.
  - Implemented live SOQL execution (`/services/data/v58.0/query`) to fetch real records directly from the live Salesforce Org, while writing raw payloads and indices to the local LocalStack AWS instance.
- **Consequences:**
  - Developers can work with actual CRM data in real-time while maintaining zero-cost local AWS storage and queuing.

---

## 💬 Discussion Notes Log

### Session 1: Project Scaffolding & Initial Setup
- **Participants:** User, Antigravity Agent
- **Decisions:** Initialized repo, docs, Docker Compose with LocalStack, and Antigravity instructions.

### Session 2: Live Salesforce Requirement Clarification
- **User Instruction:** "the salesforce going to be live even we when we are using docker"
- **Actions Taken:**
  - Upgraded [integration-engine/app/salesforce_client.py](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/integration-engine/app/salesforce_client.py) to authenticate with live Salesforce Orgs via OAuth and execute live SOQL queries.
  - Added live Salesforce credential configurations to [.env](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/.env) and [docker-compose.yml](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docker-compose.yml).
  - Updated [docs/setup-guide.md](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docs/setup-guide.md) with Live Salesforce connection steps.
