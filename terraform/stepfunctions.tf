resource "aws_cloudwatch_log_group" "stepfunctions" {
  name              = "/aws/vendedlogs/states/${local.name_prefix}"
  retention_in_days = 14

  tags = local.common_tags
}

resource "aws_sfn_state_machine" "workflow" {
  name     = "${local.name_prefix}-workflow"
  role_arn = aws_iam_role.stepfunctions_role.arn
  type     = "STANDARD"

  definition = templatefile("${path.module}/../statemachine/security_orchestration.asl.json", {
    analyzer_lambda_arn         = aws_lambda_function.analyzer.arn
    risk_scoring_lambda_arn     = aws_lambda_function.risk_scoring.arn
    findings_writer_lambda_arn  = aws_lambda_function.findings_writer.arn
    notifier_lambda_arn         = aws_lambda_function.notifier.arn
    approval_request_lambda_arn = aws_lambda_function.approval_request.arn
    remediator_lambda_arn       = aws_lambda_function.remediator.arn
  })

  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.stepfunctions.arn}:*"
    include_execution_data = true
    level                  = "ALL"
  }

  tags = local.common_tags
}
