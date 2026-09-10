data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  name = "${var.project_name}-${var.environment}"
  azs  = slice(data.aws_availability_zones.available.names, 0, 2)
}

module "networking" {
  source = "./modules/networking"

  name     = local.name
  vpc_cidr = var.vpc_cidr
  azs      = local.azs
}

module "ecr_backend" {
  source = "./modules/ecr"
  name   = "${local.name}-backend"
}

module "ecr_generator" {
  source = "./modules/ecr"
  name   = "${local.name}-generator"
}

resource "aws_security_group" "ecs" {
  name_prefix = "${local.name}-ecs-"
  description = "RetentionOS ECS application tasks"
  vpc_id      = module.networking.vpc_id
}

module "alb" {
  source = "./modules/alb"

  name                      = local.name
  vpc_id                    = module.networking.vpc_id
  public_subnet_ids         = module.networking.public_subnet_ids
  backend_security_group_id = aws_security_group.ecs.id
  certificate_arn           = var.alb_certificate_arn
}

resource "aws_vpc_security_group_ingress_rule" "ecs_from_alb" {
  security_group_id            = aws_security_group.ecs.id
  referenced_security_group_id = module.alb.security_group_id

  description = "Backend API from ALB"
  ip_protocol = "tcp"
  from_port   = 8000
  to_port     = 8000
}

resource "random_password" "db" {
  length  = 28
  special = false
}

resource "random_password" "jwt" {
  length  = 64
  special = false
}

resource "random_password" "ingest" {
  length  = 48
  special = false
}

module "rds" {
  source = "./modules/rds"

  name                     = local.name
  vpc_id                   = module.networking.vpc_id
  subnet_ids               = module.networking.data_subnet_ids
  source_security_group_id = aws_security_group.ecs.id
  instance_class           = var.db_instance_class
  db_password              = random_password.db.result
}

module "redis" {
  source = "./modules/redis"

  name                     = local.name
  vpc_id                   = module.networking.vpc_id
  subnet_ids               = module.networking.data_subnet_ids
  source_security_group_id = aws_security_group.ecs.id
  node_type                = var.redis_node_type
}

resource "aws_vpc_security_group_egress_rule" "ecs_postgres" {
  security_group_id            = aws_security_group.ecs.id
  referenced_security_group_id = module.rds.security_group_id

  description = "PostgreSQL"
  ip_protocol = "tcp"
  from_port   = 5432
  to_port     = 5432
}

resource "aws_vpc_security_group_egress_rule" "ecs_redis" {
  security_group_id            = aws_security_group.ecs.id
  referenced_security_group_id = module.redis.security_group_id

  description = "Redis TLS"
  ip_protocol = "tcp"
  from_port   = 6379
  to_port     = 6379
}

# RetentionOS requires outbound HTTPS for third-party APIs and AWS public endpoints.
# Internet egress is restricted to TCP/443; unrestricted all-protocol egress is not allowed.
# trivy:ignore:AVD-AWS-0104
resource "aws_vpc_security_group_egress_rule" "ecs_https" {
  security_group_id = aws_security_group.ecs.id

  description = "HTTPS for required external APIs and AWS endpoints"
  ip_protocol = "tcp"
  from_port   = 443
  to_port     = 443
  cidr_ipv4   = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "ecs_dns_udp" {
  security_group_id = aws_security_group.ecs.id

  description = "VPC DNS UDP"
  ip_protocol = "udp"
  from_port   = 53
  to_port     = 53
  cidr_ipv4   = var.vpc_cidr
}

resource "aws_vpc_security_group_egress_rule" "ecs_dns_tcp" {
  security_group_id = aws_security_group.ecs.id

  description = "VPC DNS TCP"
  ip_protocol = "tcp"
  from_port   = 53
  to_port     = 53
  cidr_ipv4   = var.vpc_cidr
}

resource "aws_secretsmanager_secret" "app" {
  name                    = "${local.name}/app"
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret_version" "app" {
  secret_id = aws_secretsmanager_secret.app.id

  secret_string = jsonencode({
    DATABASE_URL      = "postgresql+asyncpg://retention:${random_password.db.result}@${module.rds.endpoint}/retention"
    DATABASE_URL_SYNC = "postgresql+psycopg://retention:${random_password.db.result}@${module.rds.endpoint}/retention"
    SECRET_KEY        = random_password.jwt.result
    EVENT_INGEST_KEY  = random_password.ingest.result
  })
}

resource "aws_kms_key" "models" {
  description             = "RetentionOS model artifact encryption"
  enable_key_rotation     = true
  deletion_window_in_days = 30
}

resource "aws_kms_alias" "models" {
  name          = "alias/${local.name}-models"
  target_key_id = aws_kms_key.models.key_id
}

resource "aws_s3_bucket" "models" {
  bucket_prefix = "${local.name}-models-"
  force_destroy = false
}

resource "aws_s3_bucket_public_access_block" "models" {
  bucket = aws_s3_bucket.models.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "models" {
  bucket = aws_s3_bucket.models.id

  rule {
    bucket_key_enabled = true

    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.models.arn
    }
  }
}

resource "aws_s3_bucket_versioning" "models" {
  bucket = aws_s3_bucket.models.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_route53_record" "api_origin" {
  zone_id = var.route53_zone_id
  name    = var.api_domain_name
  type    = "A"

  alias {
    name                   = module.alb.dns_name
    zone_id                = module.alb.zone_id
    evaluate_target_health = true
  }
}

module "ecs" {
  source = "./modules/ecs"

  name                       = local.name
  aws_region                 = var.aws_region
  public_subnet_ids          = module.networking.public_subnet_ids
  security_group_id          = aws_security_group.ecs.id
  target_group_arn           = module.alb.target_group_arn
  desired_count              = var.ecs_desired_count
  event_worker_desired_count = var.event_worker_desired_count
  cpu                        = var.backend_cpu
  memory                     = var.backend_memory

  backend_image   = "${module.ecr_backend.repository_url}:${var.backend_image_tag}"
  generator_image = "${module.ecr_generator.repository_url}:${var.generator_image_tag}"

  app_secret_arn    = aws_secretsmanager_secret.app.arn
  redis_url         = "rediss://${module.redis.primary_endpoint}:6379/0"
  model_bucket      = aws_s3_bucket.models.id
  model_kms_key_arn = aws_kms_key.models.arn
  trusted_hosts     = jsonencode([var.api_domain_name, module.alb.dns_name, "localhost"])
}

module "static_site" {
  source = "./modules/static_site"

  name            = local.name
  alb_domain_name = var.api_domain_name
  alb_origin_id   = "api-alb"

  depends_on = [aws_route53_record.api_origin]
}

module "monitoring" {
  source = "./modules/monitoring"

  name         = local.name
  cluster_name = module.ecs.cluster_name
  service_name = module.ecs.service_name
}

module "scheduled_jobs" {
  count  = var.enable_scheduled_jobs ? 1 : 0
  source = "./modules/scheduled_jobs"

  name                = local.name
  cluster_arn         = module.ecs.cluster_arn
  task_definition_arn = module.ecs.backend_task_definition_arn
  subnet_ids          = module.networking.public_subnet_ids
  security_group_id   = aws_security_group.ecs.id
  execution_role_arn  = module.ecs.execution_role_arn
  task_role_arn       = module.ecs.task_role_arn
}
