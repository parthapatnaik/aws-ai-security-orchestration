variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "notification_email" {
  description = "Email address for SNS notifications"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "aws-ai-security-orchestration"
}

variable "waf_scope" {
  description = "WAF scope for the demo IP set"
  type        = string
  default     = "REGIONAL"
}
