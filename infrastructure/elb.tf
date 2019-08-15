resource "aws_lb" "this" {
  name = var.name
  internal = false
  load_balancer_type = "network"
  subnets = flatten(data.aws_subnet_ids.public[*].ids)
}

resource "aws_lb_target_group" "this" {
  name = var.name
  protocol = "TCP"
  port = "5000"
  vpc_id = var.vpc_id
  target_type = "ip"

  health_check {
    protocol = "TCP"
    port = "5000"

  }
  tags = var.tags

}

resource "aws_lb_listener" "this" {
  load_balancer_arn = aws_lb.this.arn
  port = "80"
  protocol = "TCP"

  default_action {
    target_group_arn = aws_lb_target_group.this.arn
    type = "forward"
  }

  depends_on = ["aws_lb_target_group.this"]

}


output "lb_dns_name" {
  value = aws_lb.this.dns_name
}
