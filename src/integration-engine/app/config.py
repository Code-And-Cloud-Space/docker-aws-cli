import os

# AWS LocalStack / Cloud Settings
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", os.getenv("AWS_REGION", "us-east-1"))
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "test")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localstack:4566")

# Buckets, Tables, Queues
S3_RAW_EVENTS_BUCKET = os.getenv("S3_RAW_EVENTS_BUCKET", "salesforce-raw-events")
S3_BACKUPS_BUCKET = os.getenv("S3_BACKUPS_BUCKET", "salesforce-backups")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "SalesforceSyncRecords")
SQS_INBOUND_QUEUE_NAME = os.getenv("SQS_INBOUND_QUEUE_NAME", "salesforce-inbound-queue")
SQS_DLQ_NAME = os.getenv("SQS_DLQ_NAME", "salesforce-deadletter-queue")

# Live Salesforce Configuration
SALESFORCE_AUTH_TYPE = os.getenv("SALESFORCE_AUTH_TYPE", "oauth_password") # oauth_password, oauth_client_credentials, access_token
SALESFORCE_LOGIN_URL = os.getenv("SALESFORCE_LOGIN_URL", "https://login.salesforce.com")
SALESFORCE_INSTANCE_URL = os.getenv("SALESFORCE_INSTANCE_URL", "")
SALESFORCE_USERNAME = os.getenv("SALESFORCE_USERNAME", "")
SALESFORCE_PASSWORD = os.getenv("SALESFORCE_PASSWORD", "")
SALESFORCE_SECURITY_TOKEN = os.getenv("SALESFORCE_SECURITY_TOKEN", "")
SALESFORCE_CLIENT_ID = os.getenv("SALESFORCE_CLIENT_ID", "")
SALESFORCE_CLIENT_SECRET = os.getenv("SALESFORCE_CLIENT_SECRET", "")
SALESFORCE_ACCESS_TOKEN = os.getenv("SALESFORCE_ACCESS_TOKEN", "")
SALESFORCE_API_VERSION = os.getenv("SALESFORCE_API_VERSION", "v58.0")
