# Docker

## Run full stack

### ECR Login
In order to pull the images from AWS, you must be logged into AWS ECR:
```
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 216821345641.dkr.ecr.us-east-1.amazonaws.com
```
### Docker Compose
```
docker-compose up -d
```
> If the ActiveMQ container fails to start, it might have to do with configuration initialization. See [Customizing configuration and persistence location](https://github.com/rmohr/docker-activemq#customizing-configuration-and-persistence-location).

### Logs
