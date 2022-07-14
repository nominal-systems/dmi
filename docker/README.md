# Docker

## Run full stack

### Docker Compose
```
# Development
docker-compose up -d mysql mongo activemq redis

# Production
docker-compose up -d
```
> If the ActiveMQ container fails to start, it might have to do with configuration initialization. See [Customizing configuration and persistence location](https://github.com/rmohr/docker-activemq#customizing-configuration-and-persistence-location).

### Logs
