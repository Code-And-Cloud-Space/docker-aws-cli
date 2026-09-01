# Antigravity Project Configuration: Enterprise Customer Data Synchronization

Welcome to the **Enterprise Customer Data Synchronization** project. This enterprise-grade serverless integration establishes a seamless, automated, and bidirectional flow of customer information between **Salesforce CRM** and the AWS Cloud ecosystem (**Amazon S3**, **Amazon DynamoDB**, **AWS Step Functions**, **Amazon CloudWatch**, and **AWS Secrets Manager**).

---

## 🏢 Business Context & Core Outcomes
- **Operational Efficiency**: Eliminates manual data entry by automating the bidirectional transfer of customer profile updates.
- **Unified Customer View**: Connects Salesforce with the enterprise data lake and microservices to maintain a single source of truth across sales, service, and operations.
- **Cost Reduction**: Utilizes pay-as-you-go containerized AWS Lambda functions and serverless cloud services.
- **Enhanced Security & Compliance**: Centralizes data tracking, protects credentials via AWS Secrets Manager vault, and audits all sync events in Amazon CloudWatch.

---

## 🛠️ Enterprise Toolset & Architectural Mapping
1. **Salesforce (CRM Engagement Hub)**: Front-end customer interface (`src/services/salesforceService.js`).
2. **AWS Step Functions (The Digital Project Manager)**: Workflow orchestrator managing sequence, retries, and failure states (`src/services/sfnService.js`).
3. **AWS Lambda (Task Execution Engines)**: Serverless compute executing extraction, translation, and synchronization (`src/index.js`).
4. **Amazon S3 (Secure Staging Area)**: High-capacity temporary holding zone for raw/processed batches (`src/services/s3Service.js`).
5. **Amazon DynamoDB (The Tracking Ledger)**: Sub-millisecond tracking database recording sync statuses, timestamps, and checksums (`src/services/dynamoService.js`).
6. **AWS Secrets Manager (The Digital Vault)**: Rotates and secures Salesforce OAuth credentials and API tokens (`src/services/secretsManagerService.js`).
7. **Amazon CloudWatch (Enterprise Observability)**: Emits business KPIs (`RecordsProcessed`, `BatchSyncDurationMs`) and security audit logs (`src/services/cloudwatchService.js`).

---

## 🚀 Developer Workflows & Commands
- **Run Unit Tests**: `npm test`
- **Start Full Local Stack (LocalStack + Lambda RIE)**: `npm run docker:compose`
- **Trigger Full Enterprise Batch Sync**: `npm run sync:test:full`
- **Trigger Real-time Single Customer Sync**: `npm run sync:test:realtime`
- **Trigger Bidirectional Push to Salesforce CRM**: `npm run sync:test:push-crm`
- **Inspect DynamoDB Tracking Ledger**: `npm run sync:test:ledger`
- **Inspect S3 Staged Batches**: `npm run sync:test:s3-batches`

---

## 📋 Coding Conventions
- Use modern JavaScript (ES Modules).
- AWS SDK v3 modular imports (`@aws-sdk/client-*`).
- Strict separation of service concerns in `src/services/`.
- LocalStack for offline development; automatic fallback to AWS IAM in production.
