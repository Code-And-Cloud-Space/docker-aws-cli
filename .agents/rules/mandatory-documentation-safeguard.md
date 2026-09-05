---
trigger: always_on
description: Mandatory AI documentation safeguard enforcing automatic updates to docs/ on every change.
---

# 🛡️ MANDATORY AI SAFEGUARD: CONTINUOUS DOCUMENTATION ENFORCEMENT

> [!CAUTION]
> **CRITICAL RULE FOR ALL AI AGENTS (ANTIGRAVITY, GEMINI, CLAUDE, ETC.):**
> You MUST update the `docs/` folder in the same response whenever ANY code, configuration, dependency, requirement, or architectural decision is modified or discussed.
>
> **FAILURE TO UPDATE DOCUMENTATION IS A VIOLATION OF REPOSITORY POLICY.**

---

## 📋 Mandatory Documentation Protocol

Whenever you perform an action, you MUST update the corresponding documentation file before concluding your response:

### 1. `docs/work-progress.md`
- **When to update:** Every time a task, feature, fix, virtualenv change, container modification, or milestone is started, updated, or completed.
- **What to write:**
  - Update the **Milestone Tracker table** (mark `🟢 Complete`, `🟡 In Progress`, or add new items).
  - Add an entry under the **Activity Log** for the current date describing what was done.

### 2. `docs/discussions-and-decisions.md`
- **When to update:** Whenever a new requirement is stated by the user (e.g. "remove mock", "connect to live salesforce", "add venv"), a trade-off is made, or an architectural choice is decided.
- **What to write:**
  - Create a new **Architectural Decision Record (ADR)** if it affects system design.
  - Add a note in the **Discussion Notes Log** recording the user's intent and the agent's resolution.

### 3. `docs/architecture.md`
- **When to update:** Whenever containers, network ports, data models (DynamoDB keys, S3 buckets, SQS queues), or integration flows are added, removed, or altered.
- **What to write:**
  - Keep the ASCII topology diagrams and tables accurate.

### 4. `docs/setup-guide.md`
- **When to update:** Whenever environment variables (`.env`), CLI commands, dependencies, or setup instructions change.
- **What to write:**
  - Keep testing commands, quickstart commands, and setup instructions in sync.

---

## 🔗 File Link Standard
Always provide clickable links using the `file://` scheme:
- `[docs/work-progress.md](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docs/work-progress.md)`
- `[docs/discussions-and-decisions.md](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docs/discussions-and-decisions.md)`
- `[docs/architecture.md](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docs/architecture.md)`
- `[docs/setup-guide.md](file:///Volumes/MacDisk/Docker-Projects/docker-aws-cli/docs/setup-guide.md)`
