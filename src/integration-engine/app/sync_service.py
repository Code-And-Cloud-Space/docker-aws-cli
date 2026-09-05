import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

from .aws_client import aws_manager
from .salesforce_client import sf_client
from . import config

# In-memory sync audit log
SYNC_LOGS: List[Dict[str, Any]] = []

def log_sync_event(event_type: str, status: str, details: Dict[str, Any]):
    log_entry = {
        "id": f"log-{uuid.uuid4().hex[:8]}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "eventType": event_type,
        "status": status,
        "details": details
    }
    SYNC_LOGS.insert(0, log_entry)
    if len(SYNC_LOGS) > 200:
        SYNC_LOGS.pop()
    return log_entry

async def full_sync_salesforce_to_aws() -> Dict[str, Any]:
    """Scans all Salesforce objects (Account, Contact, Opportunity, Lead) and mirrors into DynamoDB and S3"""
    sobjects = ["Account", "Contact", "Opportunity", "Lead"]
    results = {"synced_count": 0, "objects": {}}

    for sobject in sobjects:
        try:
            records = await sf_client.get_records(sobject)
            results["objects"][sobject] = len(records)
            for rec in records:
                rec_id = rec.get("Id")
                if rec_id:
                    # 1. Store in DynamoDB
                    aws_manager.upsert_sync_record(
                        sobject_type=sobject,
                        salesforceId=rec_id,
                        payload=rec,
                        sync_status="SYNCED"
                    )
                    # 2. Archive raw snapshot in S3
                    aws_manager.upload_raw_event(
                        event_id=f"fullsync-{sobject}-{rec_id}",
                        data=rec,
                        bucket=config.S3_RAW_EVENTS_BUCKET
                    )
                    results["synced_count"] += 1
            
            log_sync_event(
                event_type=f"FULL_SYNC_{sobject}",
                status="SUCCESS",
                details={"recordCount": len(records), "sobject": sobject}
            )
        except Exception as e:
            log_sync_event(
                event_type=f"FULL_SYNC_{sobject}",
                status="ERROR",
                details={"error": str(e), "sobject": sobject}
            )

    return results

async def handle_salesforce_cdc_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Receives a CDC event, enqueues to SQS, saves to S3 raw bucket, and indexes in DynamoDB"""
    event_id = event.get("eventId", f"evt-{uuid.uuid4().hex[:8]}")
    payload = event.get("payload", {})
    header = payload.get("ChangeEventHeader", {})
    sobject = header.get("entityName", "Unknown")
    record_ids = header.get("recordIds", [])
    change_type = header.get("changeType", "UPDATE")

    rec_id = record_ids[0] if record_ids else payload.get("Id", "unknown_id")

    # 1. Enqueue to SQS for async workers
    try:
        aws_manager.send_sqs_message({
            "eventId": event_id,
            "sobject": sobject,
            "recordId": rec_id,
            "changeType": change_type,
            "timestamp": event.get("timestamp"),
            "data": payload
        })
    except Exception as e:
        print(f"Failed to enqueue to SQS: {e}")

    # 2. Upload raw event to S3
    s3_path = ""
    try:
        s3_path = aws_manager.upload_raw_event(event_id=event_id, data=event)
    except Exception as e:
        print(f"Failed to upload to S3: {e}")

    # 3. Update DynamoDB
    try:
        aws_manager.upsert_sync_record(
            sobject_type=sobject,
            salesforceId=rec_id,
            payload=payload,
            sync_status="SYNCED" if change_type != "DELETE" else "DELETED"
        )
    except Exception as e:
        print(f"Failed to update DynamoDB: {e}")

    log_entry = log_sync_event(
        event_type=f"CDC_{sobject}_{change_type}",
        status="PROCESSED",
        details={
            "eventId": event_id,
            "sobject": sobject,
            "recordId": rec_id,
            "changeType": change_type,
            "s3Path": s3_path
        }
    )

    return {
        "success": True,
        "eventId": event_id,
        "s3Path": s3_path,
        "logEntry": log_entry
    }

async def push_aws_event_to_salesforce(sobject: str, payload: Dict[str, Any], record_id: str = None) -> Dict[str, Any]:
    """Pushes a record created or updated in AWS into Salesforce"""
    try:
        if record_id:
            res = await sf_client.update_record(sobject, record_id, payload)
            action = "UPDATE"
        else:
            res = await sf_client.create_record(sobject, payload)
            action = "CREATE"
            record_id = res.get("id")

        # Sync back to DynamoDB with reference
        if record_id:
            full_record = await sf_client.get_record(sobject, record_id)
            if full_record:
                aws_manager.upsert_sync_record(
                    sobject_type=sobject,
                    salesforceId=record_id,
                    payload=full_record,
                    sync_status="SYNCED"
                )

        log_sync_event(
            event_type=f"AWS_TO_SALESFORCE_{sobject}_{action}",
            status="SUCCESS",
            details={"sobject": sobject, "recordId": record_id, "payload": payload}
        )
        return {"success": True, "recordId": record_id, "action": action}
    except Exception as e:
        log_sync_event(
            event_type=f"AWS_TO_SALESFORCE_{sobject}",
            status="ERROR",
            details={"error": str(e), "payload": payload}
        )
        raise e
