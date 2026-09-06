data "aws_availability_zones" "available" { state="available" }
locals { name="${var.project_name}-${var.environment}"; azs=slice(data.aws_availability_zones.available.names,0,2) }
module "networking" { source="./modules/networking"; name=local.name; vpc_cidr=var.vpc_cidr; azs=local.azs }
module "ecr_backend" { source="./modules/ecr"; name="${local.name}-backend" }
module "ecr_generator" { source="./modules/ecr"; name="${local.name}-generator" }
module "alb" { source="./modules/alb"; name=local.name; vpc_id=module.networking.vpc_id; public_subnet_ids=module.networking.public_subnet_ids }
resource "aws_security_group" "ecs" {
  name_prefix="${local.name}-ecs-"
  vpc_id=module.networking.vpc_id
  ingress { from_port=8000; to_port=8000; protocol="tcp"; security_groups=[module.alb.security_group_id] }
  egress { from_port=0; to_port=0; protocol="-1"; cidr_blocks=["0.0.0.0/0"] }
}
module "rds" { source="./modules/rds"; name=local.name; vpc_id=module.networking.vpc_id; subnet_ids=module.networking.data_subnet_ids; source_security_group_id=aws_security_group.ecs.id; instance_class=var.db_instance_class; db_password=random_password.db.result }
module "redis" { source="./modules/redis"; name=local.name; vpc_id=module.networking.vpc_id; subnet_ids=module.networking.data_subnet_ids; source_security_group_id=aws_security_group.ecs.id; node_type=var.redis_node_type }
resource "random_password" "db" { length=28; special=false }
resource "random_password" "jwt" { length=64; special=false }
resource "random_password" "ingest" { length=48; special=false }
resource "aws_secretsmanager_secret" "app" { name="${local.name}/app"; recovery_window_in_days=0 }
resource "aws_secretsmanager_secret_version" "app" { secret_id=aws_secretsmanager_secret.app.id; secret_string=jsonencode({DATABASE_URL="postgresql+asyncpg://retention:${random_password.db.result}@${module.rds.endpoint}/retention",DATABASE_URL_SYNC="postgresql+psycopg://retention:${random_password.db.result}@${module.rds.endpoint}/retention",SECRET_KEY=random_password.jwt.result,EVENT_INGEST_KEY=random_password.ingest.result}) }
resource "aws_s3_bucket" "models" { bucket_prefix="${local.name}-models-"; force_destroy=true }
resource "aws_s3_bucket_public_access_block" "models" { bucket=aws_s3_bucket.models.id; block_public_acls=true; block_public_policy=true; ignore_public_acls=true; restrict_public_buckets=true }
resource "aws_s3_bucket_server_side_encryption_configuration" "models" { bucket=aws_s3_bucket.models.id; rule { apply_server_side_encryption_by_default { sse_algorithm="AES256" } } }
resource "aws_s3_bucket_versioning" "models" { bucket=aws_s3_bucket.models.id; versioning_configuration { status="Enabled" } }
module "ecs" {
 source="./modules/ecs"; name=local.name; aws_region=var.aws_region; public_subnet_ids=module.networking.public_subnet_ids; security_group_id=aws_security_group.ecs.id; target_group_arn=module.alb.target_group_arn; desired_count=var.ecs_desired_count; cpu=var.backend_cpu; memory=var.backend_memory
 backend_image="${module.ecr_backend.repository_url}:latest"; generator_image="${module.ecr_generator.repository_url}:latest"; app_secret_arn=aws_secretsmanager_secret.app.arn; redis_url="rediss://${module.redis.primary_endpoint}:6379/0"; model_bucket=aws_s3_bucket.models.id; trusted_hosts=jsonencode([module.alb.dns_name,"localhost"])
}
module "static_site" { source="./modules/static_site"; name=local.name; alb_domain_name=module.alb.dns_name; alb_origin_id="api-alb" }
module "monitoring" { source="./modules/monitoring"; name=local.name; cluster_name=module.ecs.cluster_name; service_name=module.ecs.service_name }
module "scheduled_jobs" { source="./modules/scheduled_jobs"; count=var.enable_scheduled_jobs?1:0; name=local.name; cluster_arn=module.ecs.cluster_arn; task_definition_arn=module.ecs.backend_task_definition_arn; subnet_ids=module.networking.public_subnet_ids; security_group_id=aws_security_group.ecs.id; execution_role_arn=module.ecs.execution_role_arn; task_role_arn=module.ecs.task_role_arn }
