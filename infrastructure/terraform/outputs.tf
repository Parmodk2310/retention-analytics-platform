output "cloudfront_domain" { value=module.static_site.cloudfront_domain }
output "frontend_bucket" { value=module.static_site.bucket_name }
output "cloudfront_distribution_id" { value=module.static_site.distribution_id }
output "backend_ecr_repository" { value=module.ecr_backend.repository_name }
output "backend_ecr_url" { value=module.ecr_backend.repository_url }
output "generator_ecr_repository" { value=module.ecr_generator.repository_name }
output "generator_ecr_url" { value=module.ecr_generator.repository_url }
output "ecs_cluster" { value=module.ecs.cluster_name }
output "ecs_service" { value=module.ecs.service_name }
output "backend_task_definition" { value=module.ecs.backend_task_definition_family }
output "generator_task_definition" { value=module.ecs.generator_task_definition_family }
output "public_subnet_ids" { value=module.networking.public_subnet_ids }
output "ecs_security_group_id" { value=aws_security_group.ecs.id }
output "rds_endpoint" { value=module.rds.endpoint; sensitive=true }
