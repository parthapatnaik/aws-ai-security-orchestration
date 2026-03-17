import os
import urllib.parse

import boto3

from common.utils import log_event


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["FINDINGS_TABLE"])
sns = boto3.client("sns")
topic_arn = os.environ["SNS_TOPIC_ARN"]
approval_base_url = os.environ["APPROVAL_BASE_URL"].rstrip("/")
approval_callback_token = os.environ["APPROVAL_CALLBACK_TOKEN"]


def lambda_handler(event, context):
    finding = event["finding"]
    task_token = event["taskToken"]
    finding_id = finding["finding_id"]

    table.update_item(
        Key={"finding_id": finding_id},
        UpdateExpression="SET #s = :s, task_token = :t, approval_required = :a",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={
            ":s": "PENDING_APPROVAL",
            ":t": task_token,
            ":a": True,
        },
    )

    approve_url = (
        f"{approval_base_url}/approval?finding_id={urllib.parse.quote(finding_id)}"
        f"&decision=approve&token={urllib.parse.quote(approval_callback_token)}"
    )
    reject_url = (
        f"{approval_base_url}/approval?finding_id={urllib.parse.quote(finding_id)}"
        f"&decision=reject&token={urllib.parse.quote(approval_callback_token)}"
    )

    message = f"""
Approval required for high-severity finding.

Finding ID: {finding_id}
Event Type: {finding.get("event_type")}
Resource ID: {finding.get("resource_id")}
Actor: {finding.get("actor")}
Severity: {finding.get("severity")}
Risk Score: {finding.get("risk_score")}
Summary: {finding.get("summary")}

Approve:
{approve_url}

Reject:
{reject_url}
""".strip()

    sns.publish(
        TopicArn=topic_arn,
        Subject=f"[APPROVAL REQUIRED] {finding.get('event_type', 'security finding')}"[:100],
        Message=message,
    )

    log_event(
        "approval_request",
        finding_id=finding_id,
        severity=finding.get("severity"),
        status="PENDING_APPROVAL",
    )
    return {
        "finding_id": finding_id,
        "status": "PENDING_APPROVAL",
        "message": "Approval request sent",
    }
