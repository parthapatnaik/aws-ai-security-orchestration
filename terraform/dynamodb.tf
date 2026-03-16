resource "aws_dynamodb_table" "findings" {
  name         = "${local.name_prefix}-findings"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "finding_id"

  attribute {
    name = "finding_id"
    type = "S"
  }

  tags = local.common_tags
}
