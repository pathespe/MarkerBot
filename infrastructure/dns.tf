data "aws_route53_zone" "this" {
  name = "arup.io."
}

resource "aws_route53_record" "this" {
  zone_id = data.aws_route53_zone.this.zone_id
  name    = "lunchtimeprogramming.${data.aws_route53_zone.this.name}"
  type    = "CNAME"
  ttl     = "60"
  records = [aws_lb.this.dns_name]
  allow_overwrite = true
}
