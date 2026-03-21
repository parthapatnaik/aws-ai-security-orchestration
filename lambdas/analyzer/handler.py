import json
import os
import uuid
from datetime import datetime, timezone

import boto3


BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")


def _enrich_with_bedrock(finding):
    """Call Amazon Bedrock (Claude) to enrich a finding with AI-generated threat analysis.
    Returns the finding dict with ai_summary, threat_category, and recommended_action added.
    On any failure, sets ai_summary to a fallback value and returns without raising."""
    prompt_event = {
        "event_type": finding.get("event_type"),
        "resource_id": finding.get("resource_id"),
        "actor": finding.get("actor"),
        "severity_hint": finding.get("severity_hint"),
        "summary": finding.get("summary"),
    }
    prompt = (
        "You are a cloud security analyst. Analyze the following security event and respond "
        "with a JSON object containing exactly three fields:\n"
        '- "threat_category": a short label (e.g. Privilege Escalation, Lateral Movement, Data Exfiltration)\n'
        '- "ai_summary": a 2-sentence risk assessment explaining the threat and its potential impact\n'
        '- "recommended_action": one concrete immediate step a responder should take\n\n'
        f"Security event: {json.dumps(prompt_event)}\n\n"
        "Respond with only the JSON object, no markdown fences."
    )
    try:
        bedrock = boto3.client("bedrock-runtime")
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        })
        response = bedrock.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=body,
        )
        response_body = json.loads(response["body"].read())
        ai_output = json.loads(response_body["content"][0]["text"])
        finding["ai_summary"] = ai_output.get("ai_summary", "No summary returned")
        finding["threat_category"] = ai_output.get("threat_category", "Unknown")
        finding["recommended_action"] = ai_output.get("recommended_action", "Investigate manually")
    except Exception as exc:
        finding["ai_summary"] = "AI enrichment unavailable"
        finding["threat_category"] = "Unknown"
        finding["recommended_action"] = "Investigate manually"
        print(json.dumps({"stage": "analyzer", "bedrock_error": str(exc)}))
    return finding


def lambda_handler(event, context):
    detail = event.get("detail", {})

    finding = {
        "finding_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": event.get("source", "unknown"),
        "event_type": detail.get("event_type", "unknown"),
        "resource_id": detail.get("resource_id", "unknown"),
        "actor": detail.get("actor", "unknown"),
        "severity_hint": detail.get("severity_hint", "medium"),
        "summary": detail.get("summary", "Security event detected"),
        "status": "OPEN",
        "raw_event": event,
    }

    finding = _enrich_with_bedrock(finding)

    print(
        json.dumps(
            {
                "stage": "analyzer",
                "finding_id": finding["finding_id"],
                "severity_hint": finding["severity_hint"],
                "status": finding["status"],
                "ai_summary": finding["ai_summary"],
                "threat_category": finding["threat_category"],
            }
        )
    )
    return finding
