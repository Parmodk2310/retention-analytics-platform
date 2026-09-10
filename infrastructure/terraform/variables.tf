variable "aws_region" {
  type    = string
  default = "ap-south-1"
}

variable "project_name" {
  type    = string
  default = "retention-analytics"
}

variable "environment" {
  type    = string
  default = "production"
}

variable "vpc_cidr" {
  type    = string
  default = "10.42.0.0/16"
}

variable "backend_cpu" {
  type    = number
  default = 512
}

variable "backend_memory" {
  type    = number
  default = 1024
}

variable "ecs_desired_count" {
  type        = number
  default     = 0
  description = "Use 0 for bootstrap before the first immutable backend image is deployed, then set to 1."
}

variable "event_worker_desired_count" {
  type        = number
  default     = 0
  description = "Use 0 for bootstrap before the first immutable backend image is deployed, then set to 1."
}

variable "backend_image_tag" {
  type        = string
  default     = "bootstrap"
  description = "Immutable backend image tag. Production deployments should use a Git commit SHA."
}

variable "generator_image_tag" {
  type        = string
  default     = "bootstrap"
  description = "Immutable generator image tag when the generator task is explicitly required."
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.micro"
}

variable "redis_node_type" {
  type    = string
  default = "cache.t4g.micro"
}

variable "enable_scheduled_jobs" {
  type    = bool
  default = false
}

variable "api_domain_name" {
  type        = string
  description = "DNS name used by CloudFront to reach the HTTPS ALB origin, for example api.example.com."
}

variable "route53_zone_id" {
  type        = string
  description = "Route53 public hosted-zone ID containing api_domain_name."
}

variable "alb_certificate_arn" {
  type        = string
  description = "ACM certificate ARN in the ALB region covering api_domain_name."
}
