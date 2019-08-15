data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

data "aws_subnet_ids" "public" {
  vpc_id = var.vpc_id
  tags = {
    Tier = "public"
  }
}

data "aws_subnet_ids" "private" {
  vpc_id = var.vpc_id
  tags = {
    Tier = "private"
  }
}

data "aws_security_group" "management" {
  tags = {
    role = "management"
  }
  vpc_id = var.vpc_id
}

variable "vpc_id" {
}

variable "name" {
}

variable "domain_name" {}

variable "tags" {}

variable "rds_username" {}

variable "rds_password" {}

variable "arup_cidrs" {}

output "repo" {
  value = aws_ecr_repository.this.repository_url
}
