data "aws_ec2_managed_prefix_list" "cloudfront_origin" {
  name = "com.amazonaws.global.cloudfront.origin-facing"
}

resource "aws_security_group" "this" {
  name_prefix = "${var.name}-alb-"
  vpc_id      = var.vpc_id

  ingress {
    description     = "HTTPS from CloudFront origin-facing network"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    prefix_list_ids = [data.aws_ec2_managed_prefix_list.cloudfront_origin.id]
  }

  egress {
    description     = "Backend API traffic only"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [var.backend_security_group_id]
  }
}

# CloudFront requires a reachable HTTPS origin. The ALB is intentionally public,
# while its security group accepts only the AWS-managed CloudFront origin-facing prefix list.
# trivy:ignore:AVD-AWS-0053
resource "aws_lb" "this" {
  name                       = substr(replace(var.name, "_", "-"), 0, 32)
  internal                   = false
  load_balancer_type         = "application"
  security_groups            = [aws_security_group.this.id]
  subnets                    = var.public_subnet_ids
  drop_invalid_header_fields = true
}

resource "aws_lb_target_group" "backend" {
  name                 = substr("${var.name}-api", 0, 32)
  port                 = 8000
  protocol             = "HTTP"
  vpc_id               = var.vpc_id
  target_type          = "ip"
  deregistration_delay = 15

  health_check {
    path                = "/api/v1/health/live"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.this.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }
}
