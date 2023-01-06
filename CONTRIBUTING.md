# Contribution guidelines


## Local Dev Setup

```sh
git clone https://github.com/OracLabs/orac
cd orac/api


# see what versions of Python are available; install 3.10+ if not available
pyenv versions
pyenv install 3.10.1

# install poetry (MAC)
curl -sSL https://install.python-poetry.org | python3 -

# install requirements
poetry install

# install pre-commit (this will use poetry virtual env)
poetry run pre-commit install

```

## Development

```sh
git clone https://github.com/online-ml/beaver
cd beaver

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
