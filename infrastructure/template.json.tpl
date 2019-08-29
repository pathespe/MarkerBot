[
  {
    "name": "${NAME}",
    "image": "${REPOSITORY_URL}:latest",
    "networkMode": "awsvpc",
    "essential": true,
    "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/${NAME}",
          "awslogs-region": "${AWS_REGION}",
          "awslogs-stream-prefix": "ecs"
        }
    },
    "portMappings": [
      {
        "containerPort": 5000,
        "hostPort": 5000
      }
    ],
    "environment": [
      {
        "name": "DATABASE_URL",
        "value": "postgresql://${DATABASE_URL}/markerbot"
      },
      {
        "name": "DB",
        "value": "${DATABASE_URL}/markerbot"
      }
    ]
  }
]
