resource "aws_iam_role" "this" {
  name = "${data.aws_region.current.name}_${var.name}"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": [
          "ec2.amazonaws.com",
          "ecs-tasks.amazonaws.com"
        ]
      },
      "Effect": "Allow"
    }
  ]
}
EOF

}

resource "aws_iam_instance_profile" "this" {
  name = "${data.aws_region.current.name}_${var.name}"
  role = aws_iam_role.this.name
}

resource "aws_iam_policy" "this" {
  name = "${data.aws_region.current.name}_${var.name}"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
      {
          "Effect": "Allow",
          "Action": [
              "iam:ListUsers",
              "iam:GetGroup",
              "iam:GetSSHPublicKey",
              "iam:ListSSHPublicKeys",
              "iam:GetUser",
              "iam:ListGroups"
          ],
          "Resource": "*"
      },
      {
          "Effect": "Allow",
          "Action": "ec2:DescribeTags",
          "Resource": "*"
      }
    ]
}
EOF

}


resource "aws_iam_role_policy_attachment" "this" {
role       = aws_iam_role.this.name
policy_arn = aws_iam_policy.this.arn
}
