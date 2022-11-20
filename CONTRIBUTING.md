# Contribution guidelines

## Development

```sh
git clone https://github.com/online-ml/beaver
cd beaver

# Run the stack
docker compose up --build -d

# See what's running
docker stats

# Follow the logs for a particular service
docker compose logs default_runner -f

# Stop
docker compose down

# Clean slate
docker compose down --rmi all -v --remove-orphans
```
