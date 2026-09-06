import os

# ==============================================================================
# AWS LocalStack & Cloud Settings
# ==============================================================================
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

# ==============================================================================
# MySQL Database Settings (Multi-User & Token Expiry Management)
# ==============================================================================
MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql-db")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "app_user")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "app_password")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "salesforce_integration")

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

# ==============================================================================
# Salesforce OAuth 2.0 Authorization Code Flow Settings
# ==============================================================================
SALESFORCE_LOGIN_URL = os.getenv("SALESFORCE_LOGIN_URL", "https://login.salesforce.com")
SALESFORCE_CLIENT_ID = os.getenv("SALESFORCE_CLIENT_ID", "")
SALESFORCE_CLIENT_SECRET = os.getenv("SALESFORCE_CLIENT_SECRET", "")
SALESFORCE_REDIRECT_URI = os.getenv("SALESFORCE_REDIRECT_URI", "http://localhost:8000/api/auth/salesforce/callback")
SALESFORCE_API_VERSION = os.getenv("SALESFORCE_API_VERSION", "v58.0")
SALESFORCE_SCOPES = os.getenv("SALESFORCE_SCOPES", "api refresh_token offline_access")

# Frontend Return URL after OAuth callback
FRONTEND_REDIRECT_URL = os.getenv("FRONTEND_REDIRECT_URL", "http://localhost:3000")
