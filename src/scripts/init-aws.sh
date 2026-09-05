#!/usr/bin/env bash
set -e

echo "=== Initializing LocalStack AWS Resources ==="

export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}
LOCALSTACK_ENDPOINT=${LOCALSTACK_ENDPOINT:-http://localstack:4566}

echo "Waiting for LocalStack endpoint at ${LOCALSTACK_ENDPOINT}..."
until curl -s "${LOCALSTACK_ENDPOINT}/_localstack/health" | grep -q "\"s3\": \"available\""; do
  echo "LocalStack S3 is not ready yet, sleeping 2 seconds..."
  sleep 2
done

echo "LocalStack is ready! Provisioning resources..."

# 1. Create S3 Buckets
echo "Creating S3 buckets..."
aws --endpoint-url="${LOCALSTACK_ENDPOINT}" s3 mb s3://salesforce-raw-events --region "${AWS_DEFAULT_REGION}" || true
aws --endpoint-url="${LOCALSTACK_ENDPOINT}" s3 mb s3://salesforce-backups --region "${AWS_DEFAULT_REGION}" || true

# 2. Create SQS Queues (DLQ first, then main queue)
echo "Creating SQS Queues..."
aws --endpoint-url="${LOCALSTACK_ENDPOINT}" sqs create-queue \
  --queue-name salesforce-deadletter-queue \
  --region "${AWS_DEFAULT_REGION}" || true

aws --endpoint-url="${LOCALSTACK_ENDPOINT}" sqs create-queue \
  --queue-name salesforce-inbound-queue \
  --region "${AWS_DEFAULT_REGION}" || true

# 3. Create DynamoDB Table
echo "Creating DynamoDB Table: SalesforceSyncRecords..."
aws --endpoint-url="${LOCALSTACK_ENDPOINT}" dynamodb create-table \
  --table-name SalesforceSyncRecords \
  --attribute-definitions \
    AttributeName=sObjectType,AttributeType=S \
    AttributeName=salesforceId,AttributeType=S \
  --key-schema \
    AttributeName=sObjectType,KeyType=HASH \
    AttributeName=salesforceId,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region "${AWS_DEFAULT_REGION}" || true

echo "=== AWS Resource Provisioning Complete ==="
