variable "aws_region" { type=string; default="ap-south-1" }
variable "project_name" { type=string; default="retention-analytics" }
variable "environment" { type=string; default="production" }
variable "vpc_cidr" { type=string; default="10.42.0.0/16" }
variable "backend_cpu" { type=number; default=512 }
variable "backend_memory" { type=number; default=1024 }
variable "ecs_desired_count" { type=number; default=0; description="Use 0 for bootstrap before the first image push, then set to 1." }
variable "db_instance_class" { type=string; default="db.t4g.micro" }
variable "redis_node_type" { type=string; default="cache.t4g.micro" }
variable "enable_scheduled_jobs" { type=bool; default=false }
