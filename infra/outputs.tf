output "s3_bucket" {
  value = aws_s3_bucket.site.bucket
}

output "cloudfront_distribution_id" {
  value = aws_cloudfront_distribution.site.id
}

output "cloudfront_domain" {
  value = aws_cloudfront_distribution.site.domain_name
}

output "nameservers" {
  description = "Set these as your domain's nameservers at your registrar"
  value       = aws_route53_zone.site.name_servers
}
