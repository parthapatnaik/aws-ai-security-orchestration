data "archive_file" "analyzer_zip" {
  type        = "zip"
  source_file = "${path.module}/../lambdas/analyzer/handler.py"
  output_path = "${path.module}/../lambdas/analyzer/analyzer.zip"
}

data "archive_file" "risk_scoring_zip" {
  type        = "zip"
  source_file = "${path.module}/../lambdas/risk_scoring/handler.py"
  output_path = "${path.module}/../lambdas/risk_scoring/risk_scoring.zip"
}

data "archive_file" "findings_writer_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../lambdas"
  output_path = "${path.module}/../lambdas/findings_writer/findings_writer.zip"
}

data "archive_file" "notifier_zip" {
  type        = "zip"
  source_file = "${path.module}/../lambdas/notifier/handler.py"
  output_path = "${path.module}/../lambdas/notifier/notifier.zip"
}

data "archive_file" "approval_request_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../lambdas"
  output_path = "${path.module}/../lambdas/approval_request/approval_request.zip"
}

data "archive_file" "approval_callback_zip" {
  type        = "zip"
  source_file = "${path.module}/../lambdas/approval_callback/handler.py"
  output_path = "${path.module}/../lambdas/approval_callback/approval_callback.zip"
}

data "archive_file" "remediator_zip" {
  type        = "zip"
  source_file = "${path.module}/../lambdas/remediator/handler.py"
  output_path = "${path.module}/../lambdas/remediator/remediator.zip"
}

resource "aws_lambda_function" "analyzer" {
  function_name    = "${local.name_prefix}-analyzer"
  role             = aws_iam_role.lambda_execution_role.arn
  runtime          = "python3.12"
  handler          = "handler.lambda_handler"
  filename         = data.archive_file.analyzer_zip.output_path
  source_code_hash = data.archive_file.analyzer_zip.output_base64sha256
  timeout          = 30

  environment {
    variables = {
      FINDINGS_TABLE = aws_dynamodb_table.findings.name
      SNS_TOPIC_ARN  = aws_sns_topic.alerts.arn
    }
  }

  tags = local.common_tags
}

resource "aws_lambda_function" "risk_scoring" {
  function_name    = "${local.name_prefix}-risk-scoring"
  role             = aws_iam_role.lambda_execution_role.arn
  runtime          = "python3.12"
  handler          = "handler.lambda_handler"
  filename         = data.archive_file.risk_scoring_zip.output_path
  source_code_hash = data.archive_file.risk_scoring_zip.output_base64sha256
  timeout          = 30

  environment {
    variables = {
      FINDINGS_TABLE = aws_dynamodb_table.findings.name
      SNS_TOPIC_ARN  = aws_sns_topic.alerts.arn
    }
  }

  tags = local.common_tags
}

resource "aws_lambda_function" "findings_writer" {
  function_name    = "${local.name_prefix}-findings-writer"
  role             = aws_iam_role.lambda_execution_role.arn
  runtime          = "python3.12"
  handler          = "findings_writer.handler.lambda_handler"
  filename         = data.archive_file.findings_writer_zip.output_path
  source_code_hash = data.archive_file.findings_writer_zip.output_base64sha256
  timeout          = 30

  environment {
    variables = {
      FINDINGS_TABLE = aws_dynamodb_table.findings.name
      SNS_TOPIC_ARN  = aws_sns_topic.alerts.arn
    }
  }

  tags = local.common_tags
}

resource "aws_lambda_function" "notifier" {
  function_name    = "${local.name_prefix}-notifier"
  role             = aws_iam_role.lambda_execution_role.arn
  runtime          = "python3.12"
  handler          = "handler.lambda_handler"
  filename         = data.archive_file.notifier_zip.output_path
  source_code_hash = data.archive_file.notifier_zip.output_base64sha256
  timeout          = 30

  environment {
    variables = {
      FINDINGS_TABLE = aws_dynamodb_table.findings.name
      SNS_TOPIC_ARN  = aws_sns_topic.alerts.arn
    }
  }

  tags = local.common_tags
}

resource "aws_lambda_function" "approval_request" {
  function_name    = "${local.name_prefix}-approval-request"
  role             = aws_iam_role.lambda_execution_role.arn
  runtime          = "python3.12"
  handler          = "approval_request.handler.lambda_handler"
  filename         = data.archive_file.approval_request_zip.output_path
  source_code_hash = data.archive_file.approval_request_zip.output_base64sha256
  timeout          = 30

  environment {
    variables = {
      FINDINGS_TABLE    = aws_dynamodb_table.findings.name
      SNS_TOPIC_ARN     = aws_sns_topic.alerts.arn
      APPROVAL_BASE_URL       = aws_api_gateway_stage.approval.invoke_url
      APPROVAL_CALLBACK_TOKEN = var.approval_callback_token
    }
  }

  tags = local.common_tags
}

resource "aws_lambda_function" "approval_callback" {
  function_name    = "${local.name_prefix}-approval-callback"
  role             = aws_iam_role.lambda_execution_role.arn
  runtime          = "python3.12"
  handler          = "handler.lambda_handler"
  filename         = data.archive_file.approval_callback_zip.output_path
  source_code_hash = data.archive_file.approval_callback_zip.output_base64sha256
  timeout          = 30

  environment {
    variables = {
      FINDINGS_TABLE          = aws_dynamodb_table.findings.name
      APPROVAL_CALLBACK_TOKEN = var.approval_callback_token
    }
  }

  tags = local.common_tags
}

resource "aws_lambda_function" "remediator" {
  function_name    = "${local.name_prefix}-remediator"
  role             = aws_iam_role.lambda_execution_role.arn
  runtime          = "python3.12"
  handler          = "handler.lambda_handler"
  filename         = data.archive_file.remediator_zip.output_path
  source_code_hash = data.archive_file.remediator_zip.output_base64sha256
  timeout          = 30

  environment {
    variables = {
      FINDINGS_TABLE  = aws_dynamodb_table.findings.name
      WAF_IP_SET_ID   = aws_wafv2_ip_set.blocked_ips.id
      WAF_IP_SET_NAME = aws_wafv2_ip_set.blocked_ips.name
      WAF_SCOPE       = var.waf_scope
      AWS_REGION_NAME = var.aws_region
    }
  }

  tags = local.common_tags
}
