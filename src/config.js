/**
 * Configuration module for Enterprise Customer Data Synchronization.
 * Supports dynamic switching between LocalStack (local dev/Docker) and AWS Cloud (production).
 */
export const config = {
  region: process.env.AWS_REGION || 'us-east-1',
  endpoint: process.env.AWS_ENDPOINT_URL || process.env.LOCALSTACK_ENDPOINT || undefined,

  // S3: Secure Staging Area for Batch Customer Data
  s3StagingBucket: process.env.S3_STAGING_BUCKET || process.env.S3_BUCKET_NAME || 'enterprise-customer-sync-staging',

  // DynamoDB: The Tracking Ledger for Synchronized Customer Records
  dynamoLedgerTable: process.env.DYNAMODB_LEDGER_TABLE || process.env.DYNAMODB_TABLE_NAME || 'CustomerSyncLedger',

  // AWS Step Functions: Workflow Orchestrator (The Digital Project Manager)
  sfnStateMachineArn: process.env.SFN_STATE_MACHINE_ARN || 'arn:aws:states:us-east-1:000000000000:stateMachine:EnterpriseCustomerSyncStateMachine',

  // AWS Secrets Manager: The Digital Vault for Salesforce & Enterprise Credentials
  salesforceSecretName: process.env.SALESFORCE_SECRET_NAME || process.env.SECRET_NAME || 'enterprise/crm/salesforce-credentials',

  // Amazon CloudWatch: Enterprise Observability & Compliance
  cloudwatchNamespace: process.env.CLOUDWATCH_NAMESPACE || 'Enterprise/CustomerSync',
  logGroupName: process.env.LOG_GROUP_NAME || '/aws/lambda/enterprise-customer-sync',

  // Environment mode
  nodeEnv: process.env.NODE_ENV || 'production',
};
