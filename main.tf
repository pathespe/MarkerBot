terraform {
  backend "s3" {
    bucket = "arupdigital-assets"
    key    = "terraform/markerbot"
    region = "ap-southeast-2"
  }
  required_version = ">= 0.12"
}

provider "aws" {
  alias  = "sydney"
  region = "ap-southeast-2"
}

module "common_tags" {
  source = "git@github.com:ArupAus/digi-infra.git//arup_regime?ref=master"
  Site       = "Lunchtime Programming"
  CostCenter = "5005-450"
  JobNumber  = "72571-05"
  Owner      = "sophie.song@arup.com"
}

module "arup_ip_ranges" {
  source = "git@github.com:ArupAus/digi-infra.git//arup-ip-ranges?ref=master"
}

module "sydney" {
  providers =  {
      aws = "aws.sydney"
  }
  source   = "./infrastructure"
  tags = module.common_tags.tags
  domain_name = "lunchtimeprogramming.arup.io"
  name = "lunchtime-sydney"
  vpc_id = "vpc-0f501f6a"
  rds_username = "muppetmuppet"
  rds_password = "muppetmuppet1"
  arup_cidrs = module.arup_ip_ranges.cidrs
}
