import json
import os

import boto3


sns = boto3.client("sns")
topic_arn = os.environ["SNS_TOPIC_ARN"]


def lambda_handler(event, context):
    subject = f"[{event.get('severity', 'unknown').upper()}] Security finding update"

    message = f"""
Security finding update

Finding ID: {event.get("finding_id")}
Event Type: {event.get("event_type")}
Resource ID: {event.get("resource_id")}
Actor: {event.get("actor")}
Severity: {event.get("severity")}
Risk Score: {event.get("risk_score")}
Summary: {event.get("summary")}
Status: {event.get("status")}
Approval Decision: {event.get("approval_status", "N/A")}
Remediation Status: {event.get("remediation_status", "N/A")}
Remediation Action: {event.get("remediation_action", "N/A")}
Remediation Target: {event.get("remediation_target", "N/A")}
""".strip()

    sns.publish(
        TopicArn=topic_arn,
        Subject=subject[:100],
        Message=message,
    )

    print(
        json.dumps(
            {
                "stage": "notifier",
                "finding_id": event.get("finding_id"),
                "severity": event.get("severity"),
                "status": event.get("status"),
            }
        )
    )
    return event
