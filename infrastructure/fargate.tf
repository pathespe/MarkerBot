resource "aws_ecr_repository" "this" {
  name = var.name
}

resource "aws_ecs_cluster" "this" {
  name = var.name
  tags = var.tags
}

data "template_file" "this" {
  template = "${file("${path.module}/template.json.tpl")}"
  vars = {
    REPOSITORY_URL = aws_ecr_repository.this.repository_url
    AWS_REGION = data.aws_region.current.name
    LOGS_GROUP = aws_cloudwatch_log_group.this.name
    NAME = var.name
    DATABASE_URL = "${var.rds_username}:${var.rds_password}@${aws_db_instance.postgres.endpoint}"
  }


  # template = file()
  # vars {
  #   REPOSITORY_URL = aws_ecr_repository.this.repository_url
  #   AWS_REGION = data.aws_region.current.name
  #   LOGS_GROUP = aws_cloudwatch_log_group.this.name
  # }
  # templatefile("${path.module}/template.json.tpl",
  #   {
  #     REPOSITORY_URL = aws_ecr_repository.this.repository_url,
  #     AWS_REGION = data.aws_region.current.name
  #     LOGS_GROUP = aws_cloudwatch_log_group.this.name
  #   }
  # )
}


resource "aws_ecs_task_definition" "this" {
  family                = var.name
  requires_compatibilities = ["FARGATE"]
  network_mode = "awsvpc"
  cpu = 256
  memory = 512
  container_definitions = data.template_file.this.rendered
  execution_role_arn = aws_iam_role.this_task.arn
  task_role_arn = aws_iam_role.this.arn
  tags = var.tags
}

resource "aws_ecs_service" "this" {
  name            = var.name
  cluster         = aws_ecs_cluster.this.id
  launch_type     = "FARGATE"
  task_definition = aws_ecs_task_definition.this.arn
  desired_count   = 1

  network_configuration {
    subnets = flatten(data.aws_subnet_ids.public[*].ids)
    security_groups = [ aws_security_group.this_ecs.id]
    assign_public_ip = true
  }


  load_balancer {
   target_group_arn = aws_lb_target_group.this.arn
   container_name = var.name
   container_port = 5000
  }

  depends_on = [
    "aws_lb_listener.this"
  ]
  propagate_tags = "SERVICE"
  tags = var.tags
}

resource "aws_iam_role" "this_task" {
  name = "${var.name}_task"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "this" {
  name = "${var.name}_assume"
  role = "${aws_iam_role.this_task.id}"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
EOF
}

resource "aws_security_group" "this_ecs" {
  name        = "${var.name}_ecs"
  description = "Allow traffic for this_ecs"
  vpc_id      = var.vpc_id

  tags = var.tags

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks     = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "this_alb" {
  name        = "${var.name}_alb"
  description = "Allow traffic for this_alb"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks     = ["0.0.0.0/0"]
  }

  tags = var.tags
}
