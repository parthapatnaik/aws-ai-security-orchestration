resource "aws_cloudwatch_event_rule" "security_events" {
  name           = "${local.name_prefix}-security-events"
  description    = "Capture custom security threat events"
  event_bus_name = "default"

  event_pattern = jsonencode({
    source        = ["custom.security"]
    "detail-type" = ["Security Threat Event"]
  })

  tags = local.common_tags
}

resource "aws_cloudwatch_event_target" "stepfunctions_target" {
  rule           = aws_cloudwatch_event_rule.security_events.name
  event_bus_name = "default"
  arn            = aws_sfn_state_machine.workflow.arn
  role_arn       = aws_iam_role.eventbridge_stepfunctions_role.arn
}
