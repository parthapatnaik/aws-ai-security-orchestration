import json
import os
from datetime import datetime, timezone

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["FINDINGS_TABLE"])
waf = boto3.client("wafv2", region_name=os.environ.get("AWS_REGION_NAME", "us-east-1"))

IP_SET_ID = os.environ["WAF_IP_SET_ID"]
IP_SET_NAME = os.environ["WAF_IP_SET_NAME"]
WAF_SCOPE = os.environ["WAF_SCOPE"]

def pick_ip(event):
    detail = ((event or {}).get("raw_event") or {}).get("detail", {})
    for key in ["ip_address", "source_ip", "ip", "client_ip"]:
        val = detail.get(key)
        if val:
            return val
    return None

def lambda_handler(event, context):
    finding_id = event.get("finding_id")
    target_ip = pick_ip(event)

    remediation_status = "SIMULATED"
    remediation_action = "NO_IP_AVAILABLE"
    remediation_target = "none"

    if target_ip:
        current = waf.get_ip_set(
            Name=IP_SET_NAME,
            Scope=WAF_SCOPE,
            Id=IP_SET_ID
        )

        addresses = list(current.get("IPSet", {}).get("Addresses", []))
        cidr = target_ip if "/" in target_ip else f"{target_ip}/32"
        if cidr not in addresses:
            addresses.append(cidr)

        waf.update_ip_set(
            Name=IP_SET_NAME,
            Scope=WAF_SCOPE,
            Id=IP_SET_ID,
            Addresses=addresses,
            LockToken=current["LockToken"]
        )

        remediation_status = "SUCCESS"
        remediation_action = "WAF_IP_BLOCK"
        remediation_target = cidr

    event["remediation_status"] = remediation_status
    event["remediation_action"] = remediation_action
    event["remediation_target"] = remediation_target
    event["remediation_timestamp"] = datetime.now(timezone.utc).isoformat()
    event["status"] = "REMEDIATED" if remediation_status == "SUCCESS" else event.get("status", "APPROVED")

    table.update_item(
        Key={"finding_id": finding_id},
        UpdateExpression="SET remediation_status = :rs, remediation_action = :ra, remediation_target = :rt, remediation_timestamp = :rts, #s = :s",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={
            ":rs": remediation_status,
            ":ra": remediation_action,
            ":rt": remediation_target,
            ":rts": event["remediation_timestamp"],
            ":s": event["status"]
        }
    )

    print(json.dumps({
        "stage": "remediator",
        "finding_id": finding_id,
        "remediation_status": remediation_status,
        "remediation_target": remediation_target
    }))
    return event
