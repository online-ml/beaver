# Contribution guidelines

## Development

```sh
git clone https://github.com/OracLabs/orac
cd orac

# Run the stack
docker compose up --build -d

# See what's running
docker stats
# or
docker-compose ps

# Follow the logs for a particular service
docker compose logs celery -f

# Stop
docker compose down

# Clean slate
docker compose down --rmi all -v --remove-orphans
```
