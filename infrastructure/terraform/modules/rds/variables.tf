variable "name" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "source_security_group_id" {
  type = string
}

variable "instance_class" {
  type = string
}

variable "db_password" {
  type      = string
  sensitive = true
}
