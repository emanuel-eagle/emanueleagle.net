# --- CloudFront Access Logs (captures raw data including geo) ---

resource "aws_s3_bucket" "logs" {
  bucket = "${var.domain_name}-cf-logs"
}

resource "aws_s3_bucket_ownership_controls" "logs" {
  bucket = aws_s3_bucket.logs.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

data "aws_canonical_user_id" "current" {}

resource "aws_s3_bucket_acl" "logs" {
  depends_on = [aws_s3_bucket_ownership_controls.logs]
  bucket     = aws_s3_bucket.logs.id

  access_control_policy {
    owner {
      id = data.aws_canonical_user_id.current.id
    }
    # Bucket owner full control
    grant {
      grantee {
        type = "CanonicalUser"
        id   = data.aws_canonical_user_id.current.id
      }
      permission = "FULL_CONTROL"
    }
    # CloudFront logs delivery account
    grant {
      grantee {
        type = "CanonicalUser"
        id   = "c4c1ede66af53448b93c283ce9448c4ba468c9432aa01d700d3878632f77d2d0"
      }
      permission = "FULL_CONTROL"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id
  rule {
    id     = "expire-old-logs"
    status = "Enabled"
    filter {}
    expiration {
      days = 90
    }
  }
}

# --- Additional CloudFront Metrics (~$2/month) ---
# Unlocks: per-error-code rates (401/403/404/502/503/504) and OriginLatency

resource "aws_cloudfront_monitoring_subscription" "site" {
  distribution_id = aws_cloudfront_distribution.site.id

  monitoring_subscription {
    realtime_metrics_subscription_config {
      realtime_metrics_subscription_status = "Enabled"
    }
  }
}

# --- CloudWatch Dashboard ---

resource "aws_cloudwatch_dashboard" "site" {
  dashboard_name = replace(var.domain_name, ".", "-")

  dashboard_body = jsonencode({
    widgets = [

      # ---- SITE TRAFFIC & PERFORMANCE ----

      {
        type   = "text"
        x      = 0
        y      = 0
        width  = 24
        height = 1
        properties = {
          markdown = "## Site Traffic & Performance"
        }
      },

      {
        type   = "metric"
        x      = 0
        y      = 1
        width  = 12
        height = 6
        properties = {
          title   = "Requests"
          view    = "timeSeries"
          stat    = "Sum"
          period  = 3600
          region  = var.aws_region
          metrics = [
            ["AWS/CloudFront", "Requests", "DistributionId", aws_cloudfront_distribution.site.id, "Region", "Global"]
          ]
        }
      },

      {
        type   = "metric"
        x      = 12
        y      = 1
        width  = 12
        height = 6
        properties = {
          title   = "Bandwidth Downloaded"
          view    = "timeSeries"
          stat    = "Sum"
          period  = 3600
          region  = var.aws_region
          metrics = [
            ["AWS/CloudFront", "BytesDownloaded", "DistributionId", aws_cloudfront_distribution.site.id, "Region", "Global"]
          ]
        }
      },

      {
        type   = "metric"
        x      = 0
        y      = 7
        width  = 12
        height = 6
        properties = {
          title   = "Cache Hit Rate (%)"
          view    = "timeSeries"
          stat    = "Average"
          period  = 3600
          region  = var.aws_region
          metrics = [
            ["AWS/CloudFront", "CacheHitRate", "DistributionId", aws_cloudfront_distribution.site.id, "Region", "Global"]
          ]
          yAxis = {
            left = { min = 0, max = 100 }
          }
        }
      },

      {
        type   = "metric"
        x      = 12
        y      = 7
        width  = 12
        height = 6
        properties = {
          title   = "Origin Latency (ms)"
          view    = "timeSeries"
          period  = 3600
          region  = var.aws_region
          metrics = [
            ["AWS/CloudFront", "OriginLatency", "DistributionId", aws_cloudfront_distribution.site.id, "Region", "Global", { stat = "p50", label = "p50" }],
            ["AWS/CloudFront", "OriginLatency", "DistributionId", aws_cloudfront_distribution.site.id, "Region", "Global", { stat = "p90", label = "p90" }],
            ["AWS/CloudFront", "OriginLatency", "DistributionId", aws_cloudfront_distribution.site.id, "Region", "Global", { stat = "p99", label = "p99" }]
          ]
        }
      },

      {
        type   = "metric"
        x      = 0
        y      = 13
        width  = 12
        height = 6
        properties = {
          title   = "Error Rates (%)"
          view    = "timeSeries"
          stat    = "Average"
          period  = 3600
          region  = var.aws_region
          metrics = [
            ["AWS/CloudFront", "4xxErrorRate", "DistributionId", aws_cloudfront_distribution.site.id, "Region", "Global", { label = "4xx" }],
            ["AWS/CloudFront", "5xxErrorRate", "DistributionId", aws_cloudfront_distribution.site.id, "Region", "Global", { label = "5xx" }],
            ["AWS/CloudFront", "TotalErrorRate", "DistributionId", aws_cloudfront_distribution.site.id, "Region", "Global", { label = "Total" }]
          ]
          yAxis = {
            left = { min = 0 }
          }
        }
      },

      {
        type   = "metric"
        x      = 12
        y      = 13
        width  = 12
        height = 6
        properties = {
          title   = "Error Breakdown (%)"
          view    = "timeSeries"
          stat    = "Average"
          period  = 3600
          region  = var.aws_region
          metrics = [
            ["AWS/CloudFront", "401ErrorRate", "DistributionId", aws_cloudfront_distribution.site.id, "Region", "Global", { label = "401 Unauthorized" }],
            ["AWS/CloudFront", "403ErrorRate", "DistributionId", aws_cloudfront_distribution.site.id, "Region", "Global", { label = "403 Forbidden" }],
            ["AWS/CloudFront", "404ErrorRate", "DistributionId", aws_cloudfront_distribution.site.id, "Region", "Global", { label = "404 Not Found" }],
            ["AWS/CloudFront", "502ErrorRate", "DistributionId", aws_cloudfront_distribution.site.id, "Region", "Global", { label = "502 Bad Gateway" }],
            ["AWS/CloudFront", "503ErrorRate", "DistributionId", aws_cloudfront_distribution.site.id, "Region", "Global", { label = "503 Unavailable" }],
            ["AWS/CloudFront", "504ErrorRate", "DistributionId", aws_cloudfront_distribution.site.id, "Region", "Global", { label = "504 Timeout" }]
          ]
        }
      },

      # ---- SPEND ----
      # Requires "Receive Billing Alerts" enabled in AWS Billing console preferences.

      {
        type   = "text"
        x      = 0
        y      = 19
        width  = 24
        height = 1
        properties = {
          markdown = "## Spend"
        }
      },

      {
        type   = "metric"
        x      = 0
        y      = 20
        width  = 12
        height = 6
        properties = {
          title   = "Total Estimated Charges (USD)"
          view    = "timeSeries"
          stat    = "Maximum"
          period  = 86400
          region  = var.aws_region
          metrics = [
            ["AWS/Billing", "EstimatedCharges", "Currency", "USD"]
          ]
        }
      },

      {
        type   = "metric"
        x      = 12
        y      = 20
        width  = 12
        height = 6
        properties = {
          title   = "Charges by Service (USD)"
          view    = "timeSeries"
          stat    = "Maximum"
          period  = 86400
          region  = var.aws_region
          metrics = [
            ["AWS/Billing", "EstimatedCharges", "ServiceName", "AmazonCloudFront", "Currency", "USD", { label = "CloudFront" }],
            ["AWS/Billing", "EstimatedCharges", "ServiceName", "AmazonS3", "Currency", "USD", { label = "S3" }],
            ["AWS/Billing", "EstimatedCharges", "ServiceName", "AmazonRoute53", "Currency", "USD", { label = "Route53" }]
          ]
        }
      }

    ]
  })
}
