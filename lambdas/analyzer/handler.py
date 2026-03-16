import json
import uuid
from datetime import datetime, timezone

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
        "raw_event": event
    }

    print(json.dumps({"stage": "analyzer", "finding": finding}))
    return finding
