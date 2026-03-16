resource "aws_wafv2_ip_set" "blocked_ips" {
  name               = "${local.name_prefix}-blocked-ips"
  description        = "Demo IP set for security orchestration remediation"
  scope              = var.waf_scope
  ip_address_version = "IPV4"
  addresses          = []

  tags = local.common_tags
}
