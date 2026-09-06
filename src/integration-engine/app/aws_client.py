import json
import boto3
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from . import config

def get_boto3_client(service_name: str):
    kwargs = {
        "region_name": config.AWS_REGION,
        "aws_access_key_id": config.AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": config.AWS_SECRET_ACCESS_KEY,
    }
    if config.AWS_ENDPOINT_URL:
        kwargs["endpoint_url"] = config.AWS_ENDPOINT_URL
    return boto3.client(service_name, **kwargs)

def get_boto3_resource(service_name: str):
    kwargs = {
        "region_name": config.AWS_REGION,
        "aws_access_key_id": config.AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": config.AWS_SECRET_ACCESS_KEY,
    }
    if config.AWS_ENDPOINT_URL:
        kwargs["endpoint_url"] = config.AWS_ENDPOINT_URL
    return boto3.resource(service_name, **kwargs)

class LocalAWSManager:
    def __init__(self):
        self.s3 = get_boto3_client("s3")
        self.dynamodb = get_boto3_resource("dynamodb")
        self.dynamodb_client = get_boto3_client("dynamodb")
        self.sqs = get_boto3_client("sqs")

    def check_health(self) -> Dict[str, Any]:
        status = {"s3": False, "dynamodb": False, "sqs": False}
        try:
            self.s3.list_buckets()
            status["s3"] = True
        except Exception:
            pass

        try:
            self.dynamodb_client.list_tables()
            status["dynamodb"] = True
        except Exception:
            pass

        try:
            self.sqs.list_queues()
            status["sqs"] = True
        except Exception:
            pass

        return status

    # S3 Helpers
    def upload_raw_event(self, event_id: str, data: Dict[str, Any], bucket: str = config.S3_RAW_EVENTS_BUCKET) -> str:
        now = datetime.now(timezone.utc)
        key = f"{now.year}/{now.month:02d}/{now.day:02d}/{event_id}.json"
        body = json.dumps(data, indent=2)
        self.s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=body,
            ContentType="application/json"
        )
        return f"s3://{bucket}/{key}"

    def list_s3_files(self, bucket: str = config.S3_RAW_EVENTS_BUCKET) -> List[Dict[str, Any]]:
        try:
            resp = self.s3.list_objects_v2(Bucket=bucket)
            files = []
            for obj in resp.get("Contents", []):
                files.append({
                    "key": obj["Key"],
                    "size": obj["Size"],
                    "lastModified": obj["LastModified"].isoformat()
                })
            return sorted(files, key=lambda x: x["lastModified"], reverse=True)
        except Exception as e:
            return []

    def get_s3_file_content(self, key: str, bucket: str = config.S3_RAW_EVENTS_BUCKET) -> Dict[str, Any]:
        """Fetches and parses the raw text/JSON content of an S3 object"""
        try:
            resp = self.s3.get_object(Bucket=bucket, Key=key)
            raw_body = resp["Body"].read().decode("utf-8")
            parsed_data = None
            try:
                parsed_data = json.loads(raw_body)
            except Exception:
                parsed_data = None

            return {
                "key": key,
                "bucket": bucket,
                "contentType": resp.get("ContentType", "application/json"),
                "size": resp.get("ContentLength", len(raw_body)),
                "lastModified": resp.get("LastModified").isoformat() if resp.get("LastModified") else None,
                "rawContent": raw_body,
                "parsedContent": parsed_data
            }
        except Exception as e:
            raise Exception(f"Failed to fetch S3 object '{key}' from bucket '{bucket}': {str(e)}")

    # DynamoDB Helpers
    def upsert_sync_record(
        self,
        sobject_type: str,
        salesforce_id: Optional[str] = None,
        payload: Dict[str, Any] = None,
        sync_status: str = "SYNCED",
        salesforceId: Optional[str] = None
    ):
        sf_id = salesforce_id or salesforceId or ""
        table = self.dynamodb.Table(config.DYNAMODB_TABLE_NAME)
        item = {
            "sObjectType": sobject_type,
            "salesforceId": sf_id,
            "awsSyncStatus": sync_status,
            "payload": json.dumps(payload or {}),
            "syncedAt": datetime.now(timezone.utc).isoformat()
        }
        table.put_item(Item=item)
        return item

    def get_all_dynamodb_records(self) -> List[Dict[str, Any]]:
        try:
            table = self.dynamodb.Table(config.DYNAMODB_TABLE_NAME)
            resp = table.scan()
            items = resp.get("Items", [])
            for item in items:
                if "payload" in item and isinstance(item["payload"], str):
                    try:
                        item["parsedPayload"] = json.loads(item["payload"])
                    except Exception:
                        pass
            return items
        except Exception:
            return []

    # SQS Helpers
    def get_queue_url(self, queue_name: str) -> Optional[str]:
        try:
            resp = self.sqs.get_queue_url(QueueName=queue_name)
            return resp.get("QueueUrl")
        except Exception:
            return None

    def send_sqs_message(self, message_body: Dict[str, Any], queue_name: str = config.SQS_INBOUND_QUEUE_NAME) -> Dict[str, Any]:
        queue_url = self.get_queue_url(queue_name)
        if not queue_url:
            raise Exception(f"Queue {queue_name} not found")
        return self.sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message_body)
        )

    def receive_sqs_messages(self, queue_name: str = config.SQS_INBOUND_QUEUE_NAME, max_messages: int = 10) -> List[Dict[str, Any]]:
        queue_url = self.get_queue_url(queue_name)
        if not queue_url:
            return []
        resp = self.sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=max_messages,
            WaitTimeSeconds=1
        )
        return resp.get("Messages", [])

    def delete_sqs_message(self, receipt_handle: str, queue_name: str = config.SQS_INBOUND_QUEUE_NAME):
        queue_url = self.get_queue_url(queue_name)
        if queue_url:
            self.sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)

    def get_sqs_stats(self) -> Dict[str, Any]:
        stats = {}
        for q in [config.SQS_INBOUND_QUEUE_NAME, config.SQS_DLQ_NAME]:
            q_url = self.get_queue_url(q)
            if q_url:
                attrs = self.sqs.get_queue_attributes(
                    QueueUrl=q_url,
                    AttributeNames=["ApproximateNumberOfMessages", "ApproximateNumberOfMessagesNotVisible"]
                ).get("Attributes", {})
                stats[q] = {
                    "availableMessages": int(attrs.get("ApproximateNumberOfMessages", 0)),
                    "inFlightMessages": int(attrs.get("ApproximateNumberOfMessagesNotVisible", 0))
                }
            else:
                stats[q] = {"status": "not_found"}
        return stats

aws_manager = LocalAWSManager()
