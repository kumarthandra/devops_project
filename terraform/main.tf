# 1. Create a VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name      = "usecase6-vpc"
    Project   = "usecase6"
    ManagedBy = "Terraform"
  }
}

# 2. Create a subnet inside the VPC
resource "aws_subnet" "main" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.subnet_cidr
  map_public_ip_on_launch = false

  tags = {
    Name      = "usecase6-subnet"
    Project   = "usecase6"
    ManagedBy = "Terraform"
  }
}

# 3. Create a security group inside the VPC
resource "aws_security_group" "main" {
  name        = "usecase6-sg"
  description = "Security group for Terraform practice"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name      = "usecase6-sg"
    Project   = "usecase6"
    ManagedBy = "Terraform"
  }
}