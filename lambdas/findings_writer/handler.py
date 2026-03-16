import json
import os
from decimal import Decimal
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["FINDINGS_TABLE"])

def convert_numbers(value):
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, dict):
        return {k: convert_numbers(v) for k, v in value.items()}
    if isinstance(value, list):
        return [convert_numbers(v) for v in value]
    return value

def lambda_handler(event, context):
    item = convert_numbers(event)
    if item.get("approval_required"):
        item["status"] = "PENDING_APPROVAL"
    table.put_item(Item=item)
    event["stored"] = True
    if event.get("approval_required"):
        event["status"] = "PENDING_APPROVAL"
    print(json.dumps({"stage": "findings_writer", "finding_id": event.get("finding_id")}))
    return event
