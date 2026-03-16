import json
import os
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["FINDINGS_TABLE"])
sfn = boto3.client("stepfunctions")


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            return float(obj)
        return super().default(obj)


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }


def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    finding_id = params.get("finding_id")
    decision = params.get("decision")

    if not finding_id or decision not in ["approve", "reject"]:
        return response(400, {"message": "Missing or invalid finding_id/decision"})

    item = table.get_item(Key={"finding_id": finding_id}).get("Item")
    if not item:
        return response(404, {"message": "Finding not found"})

    task_token = item.get("task_token")
    if not task_token:
        return response(400, {"message": "No task token stored for this finding"})

    approval_status = "APPROVED" if decision == "approve" else "REJECTED"

    table.update_item(
        Key={"finding_id": finding_id},
        UpdateExpression="SET #s = :s, approval_status = :a REMOVE task_token",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={
            ":s": approval_status,
            ":a": approval_status
        }
    )

    item["status"] = approval_status
    item["approval_status"] = approval_status
    item.pop("task_token", None)

    sfn.send_task_success(
        taskToken=task_token,
        output=json.dumps(item, cls=DecimalEncoder)
    )

    return response(200, {
        "message": f"Finding {finding_id} marked as {approval_status}"
    })
