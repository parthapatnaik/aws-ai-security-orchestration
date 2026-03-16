# AWS AI Security Orchestration

An **event-driven security orchestration and automated response platform** built using AWS serverless services.

This project demonstrates how a security event flows through an automated response pipeline:

Detection → Analysis → Risk Scoring → Human Approval → Automated Remediation

The workflow is orchestrated using **AWS Step Functions** and integrates multiple AWS services to simulate a **real-world cloud security automation platform**.

---

# Architecture Overview

Security Event  
→ EventBridge  
→ Step Functions Workflow  

Workflow Execution:

Analyzer Lambda  
→ Risk Scoring Lambda  
→ Findings Writer (DynamoDB)

Decision Path:

Low / Medium Risk  
→ SNS Notification  

High / Critical Risk  
→ Human Approval Required

Approval Workflow:

SNS Email Alert  
→ API Gateway Approval Endpoint  
→ Approval Callback Lambda  
→ Step Functions Resume Execution

Remediation:

Remediator Lambda  
→ AWS WAF IP Set Update

Final Result:

Malicious IP automatically blocked in WAF  
Security team notified.

---

# AWS Services Used

| Service | Purpose |
|------|------|
| EventBridge | Security event ingestion |
| Step Functions | Workflow orchestration |
| Lambda | Analysis, scoring, remediation |
| DynamoDB | Findings storage |
| SNS | Notifications and approvals |
| API Gateway | Approval endpoint |
| WAFv2 | Blocking malicious IPs |
| CloudWatch Logs | Observability |

---

# Repository Structure
lambdas/
analyzer/
risk_scoring/
findings_writer/
approval_request/
approval_callback/
notifier/
remediator/

statemachine/
security_orchestration.asl.json

terraform/
apigateway.tf
dynamodb.tf
eventbridge.tf
iam.tf
lambda.tf
locals.tf
outputs.tf
providers.tf
sns.tf
stepfunctions.tf
variables.tf
waf.tf


---

# Deployment

## Prerequisites
- AWS CLI configured
- Terraform installed
- Python 3.12
- AWS account with necessary permissions

---
# Deploy Infrastructure
Navigate to the terraform directory:
cd terraform

Initialize Terraform:
terraform init

Review the infrastructure plan:
terraform plan

Deploy the infrastructure:
terraform apply


Terraform will provision:

- Lambda functions
- Step Functions workflow
- EventBridge rule
- DynamoDB table
- SNS topics
- API Gateway endpoint
- WAF IP Set

---
# Example Security Event Flow
1. Security event generated
2. EventBridge triggers Step Functions workflow
3. Analyzer Lambda processes the event
4. Risk scoring evaluates severity
5. Findings stored in DynamoDB
6. High severity findings require human approval
7. Approved events trigger remediation
8. Remediator Lambda updates AWS WAF IP set
9. Malicious IP is blocked

Example blocked IP:203.0.113.10/32


---

# Learning Objectives

This project demonstrates:

- Event-driven architecture
- Security automation
- Serverless workflow orchestration
- Human-in-the-loop security approval
- Automated remediation
- Infrastructure as Code using Terraform

---
# Future Improvements
Possible enhancements include:
- GuardDuty integration
- Security Hub integration
- LLM-powered threat analysis
- SIEM integration
- Multi-account security orchestration
- Automated incident investigation

---
# Author
Partha Patnaik
AWS Cloud Architect | DevOps | Cloud Security
GitHub:  
https://github.com/parthapatnaik
