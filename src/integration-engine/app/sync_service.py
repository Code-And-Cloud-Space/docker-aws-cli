import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

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

import json
from .database import (
    SessionLocal,
    SalesforceAccount,
    SalesforceContact,
    SalesforceOpportunity
)

def upsert_crm_record_to_mysql(sobject: str, rec: Dict[str, Any]):
    """Synchronizes Salesforce CRM record into local MySQL tables"""
    sf_id = rec.get("Id")
    if not sf_id:
        return

    db = SessionLocal()
    try:
        if sobject == "Account":
            account = db.query(SalesforceAccount).filter(SalesforceAccount.salesforce_id == sf_id).first()
            if not account:
                account = SalesforceAccount(salesforce_id=sf_id)
                db.add(account)
            account.name = rec.get("Name") or "Unnamed Account"
            account.type = rec.get("Type")
            account.industry = rec.get("Industry")
            account.phone = rec.get("Phone")
            account.website = rec.get("Website")
            account.annual_revenue = str(rec.get("AnnualRevenue", "")) if rec.get("AnnualRevenue") is not None else None
            account.billing_street = rec.get("BillingStreet")
            account.billing_city = rec.get("BillingCity")
            account.billing_state = rec.get("BillingState")
            account.billing_postal_code = rec.get("BillingPostalCode")
            account.billing_country = rec.get("BillingCountry")
            account.raw_payload = json.dumps(rec)
            account.sync_status = "SYNCED"
            db.commit()

        elif sobject == "Contact":
            contact = db.query(SalesforceContact).filter(SalesforceContact.salesforce_id == sf_id).first()
            if not contact:
                contact = SalesforceContact(salesforce_id=sf_id)
                db.add(contact)
            contact.account_salesforce_id = rec.get("AccountId")
            contact.first_name = rec.get("FirstName")
            contact.last_name = rec.get("LastName") or "Unknown"
            contact.name = rec.get("Name") or f"{rec.get('FirstName', '')} {rec.get('LastName', '')}".strip()
            contact.email = rec.get("Email")
            contact.phone = rec.get("Phone")
            contact.mobile_phone = rec.get("MobilePhone")
            contact.title = rec.get("Title")
            contact.department = rec.get("Department")
            contact.raw_payload = json.dumps(rec)
            contact.sync_status = "SYNCED"
            db.commit()

        elif sobject == "Opportunity":
            opp = db.query(SalesforceOpportunity).filter(SalesforceOpportunity.salesforce_id == sf_id).first()
            if not opp:
                opp = SalesforceOpportunity(salesforce_id=sf_id)
                db.add(opp)
            opp.account_salesforce_id = rec.get("AccountId")
            opp.name = rec.get("Name") or "Unnamed Opportunity"
            opp.stage_name = rec.get("StageName") or "Prospecting"
            opp.amount = str(rec.get("Amount", "")) if rec.get("Amount") is not None else None
            opp.probability = str(rec.get("Probability", "")) if rec.get("Probability") is not None else None
            opp.type = rec.get("Type")
            opp.lead_source = rec.get("LeadSource")
            opp.raw_payload = json.dumps(rec)
            opp.sync_status = "SYNCED"
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"[MySQL Sync] Error upserting {sobject} {sf_id}: {e}")
    finally:
        db.close()

async def sync_single_salesforce_record(sobject: str, record_id: str, access_token: str, instance_url: str) -> Dict[str, Any]:
    """Fetches a specific Salesforce record and synchronizes to MySQL, DynamoDB, and S3"""
    record = await sf_client.get_record(sobject, record_id, access_token=access_token, instance_url=instance_url)
    if not record:
        raise Exception(f"Record {record_id} not found in Salesforce.")

    # 1. Sync to local MySQL DB
    upsert_crm_record_to_mysql(sobject, record)

    # 2. Sync to DynamoDB
    aws_manager.upsert_sync_record(
        sobject_type=sobject,
        salesforceId=record_id,
        payload=record,
        sync_status="SYNCED"
    )

    # 3. Archive to S3
    s3_key = aws_manager.upload_raw_event(
        event_id=f"sync-{sobject}-{record_id}",
        data=record,
        bucket=config.S3_RAW_EVENTS_BUCKET
    )

    log_sync_event(
        event_type=f"SYNC_RECORD_{sobject}",
        status="SUCCESS",
        details={"sobject": sobject, "recordId": record_id, "s3Key": s3_key}
    )

    return {
        "success": True,
        "sobject": sobject,
        "recordId": record_id,
        "mysqlSynced": True,
        "dynamoSynced": True,
        "s3Synced": True,
        "record": record
    }

async def full_sync_salesforce_to_aws(access_token: str, instance_url: str) -> Dict[str, Any]:
    """Scans all Salesforce objects (Account, Contact, Opportunity, Lead) and mirrors to MySQL, DynamoDB, and S3"""
    sobjects = ["Account", "Contact", "Opportunity", "Lead"]
    results = {"synced_count": 0, "objects": {}}

    for sobject in sobjects:
        try:
            records = await sf_client.get_records(sobject, access_token=access_token, instance_url=instance_url)
            results["objects"][sobject] = len(records)
            for rec in records:
                rec_id = rec.get("Id")
                if rec_id:
                    # 1. Upsert into MySQL Table (if Account, Contact, Opportunity)
                    upsert_crm_record_to_mysql(sobject, rec)

                    # 2. Store in DynamoDB
                    aws_manager.upsert_sync_record(
                        sobject_type=sobject,
                        salesforceId=rec_id,
                        payload=rec,
                        sync_status="SYNCED"
                    )
                    # 3. Archive raw snapshot in S3
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

async def push_aws_event_to_salesforce(
    sobject: str,
    payload: Dict[str, Any],
    access_token: str,
    instance_url: str,
    record_id: Optional[str] = None
) -> Dict[str, Any]:
    """Pushes a record created or updated in AWS into Salesforce and mirrors to MySQL & DynamoDB"""
    try:
        if record_id:
            res = await sf_client.update_record(sobject, record_id, payload, access_token=access_token, instance_url=instance_url)
            action = "UPDATE"
        else:
            res = await sf_client.create_record(sobject, payload, access_token=access_token, instance_url=instance_url)
            action = "CREATE"
            record_id = res.get("id")

        if record_id:
            full_record = await sf_client.get_record(sobject, record_id, access_token=access_token, instance_url=instance_url)
            if full_record:
                upsert_crm_record_to_mysql(sobject, full_record)
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

