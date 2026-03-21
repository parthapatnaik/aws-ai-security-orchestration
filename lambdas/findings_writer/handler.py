import os

import boto3

from common.utils import convert_numbers, log_event


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["FINDINGS_TABLE"])


def lambda_handler(event, context):
    item = convert_numbers(event)
    if item.get("approval_required"):
        item["status"] = "PENDING_APPROVAL"

    table.put_item(Item=item)

    event["stored"] = True
    if event.get("approval_required"):
        event["status"] = "PENDING_APPROVAL"

    log_event(
        "findings_writer",
        finding_id=event.get("finding_id"),
        severity=event.get("severity"),
        status=event.get("status"),
        stored=True,
    )
    return event
