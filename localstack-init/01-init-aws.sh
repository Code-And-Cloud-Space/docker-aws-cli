#!/bin/bash
set -euo pipefail

echo "=========================================================================="
echo "Initializing LocalStack AWS Mock Services for Enterprise Customer Sync"
echo "=========================================================================="

# 1. Create S3 Staging Bucket (The Secure Staging Area)
echo "[1/5] Provisioning Amazon S3 Staging Bucket: enterprise-customer-sync-staging..."
awslocal s3 mb s3://enterprise-customer-sync-staging || true

# 2. Create DynamoDB Tracking Ledger Table
echo "[2/5] Provisioning Amazon DynamoDB Tracking Ledger: CustomerSyncLedger..."
awslocal dynamodb create-table \
    --table-name CustomerSyncLedger \
    --attribute-definitions \
        AttributeName=customerId,AttributeType=S \
    --key-schema \
        AttributeName=customerId,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST || true

# 3. Create Secrets Manager Vault (The Digital Vault)
echo "[3/5] Provisioning AWS Secrets Manager Vault: enterprise/crm/salesforce-credentials..."
awslocal secretsmanager create-secret \
    --name enterprise/crm/salesforce-credentials \
    --description "Enterprise Salesforce CRM OAuth 2.0 Credentials & Access Tokens" \
    --secret-string '{
        "clientId": "3MVG9...sample_salesforce_client_id",
        "clientSecret": "mock_salesforce_client_secret_9988",
        "instanceUrl": "https://enterprise-sample.salesforce.com",
        "username": "integration.user@enterprise.org",
        "securityToken": "local_secure_token_abc123"
    }' || true

# 4. Create CloudWatch Log Group (Enterprise Observability)
echo "[4/5] Provisioning Amazon CloudWatch Log Group: /aws/lambda/enterprise-customer-sync..."
awslocal logs create-log-group --log-group-name /aws/lambda/enterprise-customer-sync || true

# 5. Create Step Functions Orchestrator (The Digital Project Manager)
echo "[5/5] Provisioning AWS Step Functions State Machine: EnterpriseCustomerSyncStateMachine..."
cat << 'SFN_SPEC' > /tmp/enterprise-sync-statemachine.json
{
  "Comment": "Enterprise Customer Data Synchronization Orchestrator",
  "StartAt": "AuthenticateVault",
  "States": {
    "AuthenticateVault": {
      "Type": "Pass",
      "Result": {
        "status": "AUTHENTICATED",
        "vault": "AWS Secrets Manager",
        "target": "Salesforce CRM"
      },
      "ResultPath": "$.vaultAuth",
      "Next": "StageBatchInS3"
    },
    "StageBatchInS3": {
      "Type": "Pass",
      "Result": {
        "status": "STAGED",
        "bucket": "enterprise-customer-sync-staging",
        "stagedAt": "2026-09-02T00:00:00Z"
      },
      "ResultPath": "$.staging",
      "Next": "TransformAndValidate"
    },
    "TransformAndValidate": {
      "Type": "Pass",
      "Result": {
        "status": "TRANSFORMED",
        "unifiedSchema": "EnterpriseUnifiedCustomerSchema",
        "validationErrors": 0
      },
      "ResultPath": "$.transformation",
      "Next": "UpdateDynamoLedger"
    },
    "UpdateDynamoLedger": {
      "Type": "Pass",
      "Result": {
        "status": "LEDGER_COMMITTED",
        "ledgerTable": "CustomerSyncLedger",
        "syncStatus": "SYNCED"
      },
      "ResultPath": "$.ledger",
      "Next": "EmitCloudWatchMetrics"
    },
    "EmitCloudWatchMetrics": {
      "Type": "Pass",
      "Result": {
        "status": "METRICS_EMITTED",
        "namespace": "Enterprise/CustomerSync",
        "compliance": "SOC2_AUDIT_LOGGED"
      },
      "ResultPath": "$.observability",
      "Next": "SyncCompleted"
    },
    "SyncCompleted": {
      "Type": "Pass",
      "End": true
    }
  }
}
SFN_SPEC

awslocal stepfunctions create-state-machine \
    --name EnterpriseCustomerSyncStateMachine \
    --definition file:///tmp/enterprise-sync-statemachine.json \
    --role-arn arn:aws:iam::000000000000:role/EnterpriseSyncExecutionRole || true

echo "=========================================================================="
echo "All Enterprise AWS Mock Services Initialized Successfully in LocalStack!"
echo "=========================================================================="
