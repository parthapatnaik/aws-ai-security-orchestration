# AWS AI Security Orchestration

An event-driven security orchestration and automated response platform built on AWS.

This project demonstrates how a security event can be:

Detection → Analysis → Risk Scoring → Human Approval → Automated Remediation.

The workflow is orchestrated using AWS Step Functions and integrates multiple AWS services to simulate a real-world security response platform.

---
# Architecture Overview

Security Event
→ EventBridge  
→ Step Functions Workflow  

Workflow:
Analyzer Lambda  
→ Risk Scoring Lambda  
→ Findings Writer (DynamoDB)

Decision:
Low / Medium  
→ SNS Notification

High / Critical  
→ Human Approval

Approval Process:
SNS Email  
→ API Gateway Approval Endpoint  
→ Approval Callback Lambda  
→ Step Functions Resume

Approved events trigger remediation:
Remediator Lambda  
→ AWS WAF IP Set Update

Final result:
Blocked IP + Notification.

---

# AWS Services Used
- EventBridge
- Step Functions
- Lambda
- DynamoDB
- SNS
- API Gateway
- WAFv2
- CloudWatch Logs

---

# Repository Structure
