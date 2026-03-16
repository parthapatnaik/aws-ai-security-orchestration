output "approval_api_invoke_url" {
  value = aws_api_gateway_stage.approval.invoke_url
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.findings.name
}

output "eventbridge_rule_name" {
  value = aws_cloudwatch_event_rule.security_events.name
}

output "sns_topic_arn" {
  value = aws_sns_topic.alerts.arn
}

output "stepfunctions_state_machine_arn" {
  value = aws_sfn_state_machine.workflow.arn
}

output "waf_ip_set_arn" {
  value = aws_wafv2_ip_set.blocked_ips.arn
}

output "waf_ip_set_name" {
  value = aws_wafv2_ip_set.blocked_ips.name
}
