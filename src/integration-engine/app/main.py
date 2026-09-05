import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import config
from .aws_client import aws_manager
from .salesforce_client import sf_client
from .sync_service import (
    full_sync_salesforce_to_aws,
    handle_salesforce_cdc_event,
    push_aws_event_to_salesforce,
    log_sync_event,
    SYNC_LOGS
)

app = FastAPI(
    title="Salesforce <-> AWS Integration Engine",
    description="Middleware handling bidirectional sync between Live Salesforce and AWS (S3, DynamoDB, SQS)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AWSToSalesforcePayload(BaseModel):
    sobject: str
    record_id: Optional[str] = None
    data: Dict[str, Any]

@app.get("/")
def root():
    return {
        "service": "Salesforce <-> AWS Integration Engine",
        "status": "online",
        "aws_endpoint": config.AWS_ENDPOINT_URL,
        "salesforce_instance": sf_client.instance_url or config.SALESFORCE_INSTANCE_URL
    }

# Health Check & Service Status
@app.get("/api/status")
async def get_system_status():
    aws_health = aws_manager.check_health()
    sf_healthy = False
    sf_instance = sf_client.instance_url or config.SALESFORCE_INSTANCE_URL
    try:
        token = await sf_client.authenticate()
        sf_healthy = bool(token)
        sf_instance = sf_client.instance_url
    except Exception as e:
        print(f"Salesforce health check error: {e}")

    return {
        "salesforce": {
            "status": "connected" if sf_healthy else "disconnected",
            "instance_url": sf_instance,
            "auth_type": config.SALESFORCE_AUTH_TYPE
        },
        "aws": {
            "status": "connected" if any(aws_health.values()) else "error",
            "services": aws_health,
            "region": config.AWS_REGION,
            "endpoint": config.AWS_ENDPOINT_URL
        },
        "recentLogsCount": len(SYNC_LOGS)
    }

# 1. Trigger Full Sync from Live Salesforce to AWS
@app.post("/api/sync/salesforce-to-aws")
async def trigger_full_sync():
    try:
        result = await full_sync_salesforce_to_aws()
        return {"status": "success", "summary": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. Push from AWS / Manual into Live Salesforce
@app.post("/api/sync/aws-to-salesforce")
async def trigger_aws_to_sf(payload: AWSToSalesforcePayload):
    try:
        result = await push_aws_event_to_salesforce(
            sobject=payload.sobject,
            payload=payload.data,
            record_id=payload.record_id
        )
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. Create Record in Live Salesforce
@app.post("/api/salesforce/records/{sobject}")
async def create_salesforce_record(sobject: str, payload: Dict[str, Any]):
    try:
        res = await sf_client.create_record(sobject, payload)
        record_id = res.get("id")
        
        # Mirror automatically into DynamoDB and S3 raw events
        if record_id:
            full_rec = await sf_client.get_record(sobject, record_id)
            if full_rec:
                aws_manager.upsert_sync_record(
                    sobject_type=sobject,
                    salesforceId=record_id,
                    payload=full_rec,
                    sync_status="SYNCED"
                )
                aws_manager.upload_raw_event(
                    event_id=f"created-{sobject}-{record_id}",
                    data=full_rec
                )
        
        log_sync_event(
            event_type=f"SALESFORCE_CREATE_{sobject}",
            status="SUCCESS",
            details={"sobject": sobject, "recordId": record_id, "payload": payload}
        )
        return {"id": record_id, "success": True, "result": res}
    except Exception as e:
        log_sync_event(
            event_type=f"SALESFORCE_CREATE_{sobject}",
            status="ERROR",
            details={"error": str(e), "payload": payload}
        )
        raise HTTPException(status_code=500, detail=str(e))

# 4. Salesforce CDC / Webhook Ingestion
@app.post("/api/webhook/salesforce-cdc")
async def salesforce_cdc_webhook(event: Dict[str, Any], background_tasks: BackgroundTasks):
    result = await handle_salesforce_cdc_event(event)
    return result

# 5. View Salesforce Records (Live SOQL proxy)
@app.get("/api/salesforce/records/{sobject}")
async def get_salesforce_records(sobject: str):
    try:
        records = await sf_client.get_records(sobject)
        return {"sobject": sobject, "totalSize": len(records), "records": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 6. View DynamoDB Sync Records
@app.get("/api/aws/dynamodb/records")
def get_dynamodb_records():
    records = aws_manager.get_all_dynamodb_records()
    return {"total": len(records), "records": records}

# 7. View S3 Files in Raw Events Bucket
@app.get("/api/aws/s3/files")
def get_s3_files(bucket: Optional[str] = None):
    target_bucket = bucket or config.S3_RAW_EVENTS_BUCKET
    files = aws_manager.list_s3_files(bucket=target_bucket)
    return {"bucket": target_bucket, "totalFiles": len(files), "files": files}

# 8. View SQS Stats
@app.get("/api/aws/sqs/stats")
def get_sqs_stats():
    return aws_manager.get_sqs_stats()

# 9. View Live Audit Logs
@app.get("/api/logs")
def get_sync_logs(limit: int = 50):
    return {"logs": SYNC_LOGS[:limit]}
