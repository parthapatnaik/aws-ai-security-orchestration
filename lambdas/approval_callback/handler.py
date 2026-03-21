import json
import os
from decimal import Decimal

import boto3


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["FINDINGS_TABLE"])
sfn = boto3.client("stepfunctions")
APPROVAL_CALLBACK_TOKEN = os.environ["APPROVAL_CALLBACK_TOKEN"]


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
        "body": json.dumps(body),
    }


def validate_request_params(params, expected_token):
    finding_id = params.get("finding_id")
    decision = params.get("decision")
    token = params.get("token")

    if not finding_id:
        return False, "Missing finding_id"
    if decision not in ["approve", "reject"]:
        return False, "Invalid decision"
    if token != expected_token:
        return False, "Invalid approval token"
    return True, "ok"


def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}
    is_valid, reason = validate_request_params(params, APPROVAL_CALLBACK_TOKEN)
    if not is_valid:
        code = 403 if reason == "Invalid approval token" else 400
        return response(code, {"message": reason})

    finding_id = params["finding_id"]
    decision = params["decision"]

    item = table.get_item(Key={"finding_id": finding_id}).get("Item")
    if not item:
        return response(404, {"message": "Finding not found"})

    task_token = item.get("task_token")
    if not task_token:
        return response(
            200,
            {
                "message": f"Finding {finding_id} was already processed",
                "status": item.get("status", "UNKNOWN"),
            },
        )

    approval_status = "APPROVED" if decision == "approve" else "REJECTED"

    table.update_item(
        Key={"finding_id": finding_id},
        UpdateExpression="SET #s = :s, approval_status = :a REMOVE task_token",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":s": approval_status, ":a": approval_status},
    )

    item["status"] = approval_status
    item["approval_status"] = approval_status
    item.pop("task_token", None)

    try:
        sfn.send_task_success(
            taskToken=task_token,
            output=json.dumps(item, cls=DecimalEncoder),
        )
    except sfn.exceptions.InvalidToken:
        return response(
            200,
            {
                "message": f"Finding {finding_id} marked as {approval_status}, but workflow token was invalid"
            },
        )
    except sfn.exceptions.TaskTimedOut:
        return response(
            200,
            {
                "message": f"Finding {finding_id} marked as {approval_status}, but workflow task timed out"
            },
        )

    return response(200, {"message": f"Finding {finding_id} marked as {approval_status}"})
