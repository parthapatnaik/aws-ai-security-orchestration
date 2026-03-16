resource "aws_api_gateway_rest_api" "approval" {
  name        = "${local.name_prefix}-approval-api"
  description = "Approval callback API for security orchestration"
}

resource "aws_api_gateway_resource" "approval" {
  rest_api_id = aws_api_gateway_rest_api.approval.id
  parent_id   = aws_api_gateway_rest_api.approval.root_resource_id
  path_part   = "approval"
}

resource "aws_api_gateway_method" "approval_get" {
  rest_api_id   = aws_api_gateway_rest_api.approval.id
  resource_id   = aws_api_gateway_resource.approval.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "approval_get" {
  rest_api_id             = aws_api_gateway_rest_api.approval.id
  resource_id             = aws_api_gateway_resource.approval.id
  http_method             = aws_api_gateway_method.approval_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.approval_callback.invoke_arn
}

resource "aws_api_gateway_deployment" "approval" {
  depends_on = [aws_api_gateway_integration.approval_get]

  rest_api_id = aws_api_gateway_rest_api.approval.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.approval.id,
      aws_api_gateway_method.approval_get.id,
      aws_api_gateway_integration.approval_get.id
    ]))
  }
}

resource "aws_api_gateway_stage" "approval" {
  deployment_id = aws_api_gateway_deployment.approval.id
  rest_api_id   = aws_api_gateway_rest_api.approval.id
  stage_name    = "prod"
}
