import json


def lambda_handler(event, context):
    event_type = event.get("event_type", "")
    severity_hint = event.get("severity_hint", "medium")

    score = 50
    severity = "medium"
    reasons = []

    if event_type == "iam_policy_change":
        score = 85
        severity = "high"
        reasons.append("IAM policy change on potentially privileged resource")

    if severity_hint == "critical":
        score = 95
        severity = "critical"
        reasons.append("Severity hint marked as critical")
    elif severity_hint == "high" and severity != "critical":
        score = max(score, 80)
        severity = "high"
        reasons.append("Severity hint marked as high")

    event["risk_score"] = score
    event["severity"] = severity
    event["risk_reason"] = reasons or ["Default scoring logic applied"]
    event["approval_required"] = severity in ["high", "critical"]

    print(
        json.dumps(
            {
                "stage": "risk_scoring",
                "finding_id": event.get("finding_id"),
                "severity": event.get("severity"),
                "risk_score": event.get("risk_score"),
                "approval_required": event.get("approval_required"),
            }
        )
    )
    return event
