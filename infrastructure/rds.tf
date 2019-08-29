resource "aws_db_instance" "postgres" {
  engine                    = "postgres"
  engine_version            = "9.6.11"
  identifier                = var.name
  instance_class            = "db.t3.micro"
  allocated_storage         = 5
  multi_az                  = false
  publicly_accessible       = true
  vpc_security_group_ids    = [aws_security_group.this.id]
  db_subnet_group_name      = aws_db_subnet_group.this.id
  final_snapshot_identifier = "${var.name}-final-snapshot"
  username                  = var.rds_username
  password                  = var.rds_password

  backup_retention_period   = 35
  backup_window   = "07:00-09:00"


  lifecycle {
    //prevent_destroy = true
  }

  tags                      = var.tags
}


resource "aws_db_subnet_group" "this" {
  name       = var.name
  subnet_ids = flatten(data.aws_subnet_ids.public[*].ids)
  tags = var.tags
}


resource "aws_security_group" "this" {
  name = var.name
  tags = var.tags
  description = "terraform-managed"
  vpc_id = var.vpc_id

  # Only postgres in
  ingress {
    from_port = 5432
    to_port = 5432
    protocol = "tcp"
    cidr_blocks = var.arup_cidrs
    self = true
  }

  ingress {
    from_port = 5432
    to_port = 5432
    protocol = "tcp"
    security_groups = [
      data.aws_security_group.management.id,
      aws_security_group.this_ecs.id      
    ]
  }

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
