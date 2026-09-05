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
  - Configured `integration-engine` with multi-mode live Salesforce authentication (OAuth 2.0 Username + Password, Client Credentials, Access Token).
  - Removed mock simulator.

---

### ADR-005: Mandatory AI Safeguard for Continuous Documentation
- **Date:** 2026-09-05
- **Status:** Accepted
- **Context:**
  As projects evolve with AI pair programmers, documentation often drifts from code changes unless strictly enforced at the agent system/rule level.
- **Decision:**
  - Created persistent, always-on Antigravity rule file: [`.agents/rules/mandatory-documentation-safeguard.md`](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/.agents/rules/mandatory-documentation-safeguard.md).
  - Consolidated agent rules under `.agents/`.

---

### ADR-006: Monorepo `src/` Module Hierarchy & Vercel CLI Development Server
- **Date:** 2026-09-05
- **Status:** Accepted
- **Context:**
  The user requested:
  1. Consolidate all application source code under a single `src/` folder containing sub-modules.
  2. Replace the Nginx container with **Vercel CLI** (`vercel dev`) for serving the local UI dashboard, enabling modern serverless/Vercel-native development and hot-reloading.
- **Decision:**
  - Scaffolding restructured to `src/`:
    - `src/integration-engine/`: Python FastAPI sync middleware.
    - `src/dashboard-ui/`: Vercel CLI powered dashboard runtime (`package.json`, `vercel.json`, `Dockerfile`).
    - `src/scripts/`: Initialization and provisioning scripts (`init-aws.sh`).
  - Replaced Nginx with `vercel dev --listen 0.0.0.0:3000 --yes` inside `src/dashboard-ui/Dockerfile`.
- **Consequences:**
  - Clean modular organization where all development code resides in `src/`.
  - Zero Nginx configuration overhead and direct alignment with Vercel deployment workflows.

---

## 💬 Discussion Notes Log

### Session 1: Project Scaffolding & Initial Setup
- **Participants:** User, Antigravity Agent
- **Decisions:** Initialized repo, docs, Docker Compose with LocalStack, and Antigravity instructions.

### Session 2: Live Salesforce Requirement Clarification
- **User Instruction:** "the salesforce going to be live even we when we are using docker"
- **Actions Taken:** Upgraded `salesforce_client.py` for live OAuth and SOQL; updated `.env` and `docker-compose.yml`.

### Session 3: Mock Removal & Python Virtual Environment Setup
- **User Instructions:** "will you remove salesforce mock", "setup venv enviroment as well"
- **Actions Taken:** Removed mock service; created `.venv` and installed dependencies from `requirements.txt`.

### Session 4: AI Documentation Safeguard & Folder Consolidation
- **User Instructions:** "make a safe guard for ai so it will update the docuemnt every time", "why there are two folder for agent"
- **Actions Taken:** Created `.agents/rules/mandatory-documentation-safeguard.md`, updated `AGENTS.md`/`GEMINI.md`, removed redundant `.agent/` folder.

### Session 5: Vercel CLI Migration & `src/` Module Restructuring
- **User Instruction:** "instead of nignx i want you to use vercel cli also i want the all developemnt i one folder under that folder sub folder as a module like we have write now"
- **Actions Taken:**
  - Moved all services into `src/` (`src/integration-engine`, `src/dashboard-ui`, `src/scripts`).
  - Swapped Nginx for Vercel CLI in `src/dashboard-ui/` with `package.json` and `vercel.json`.
  - Updated `docker-compose.yml` build contexts and volume paths.
  - Recorded ADR-006.
