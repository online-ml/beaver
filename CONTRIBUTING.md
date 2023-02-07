# Contribution guidelines


## Local Dev Setup

```sh
git clone https://github.com/OracLabs/orac
cd orac/api


# to manage multiple python versions easily use pyenv.
# see what versions of Python are available; install 3.10+ if not available
pyenv versions
pyenv install 3.11.1
pyenv local 3.11.1 

# install poetry (MAC)
curl -sSL https://install.python-poetry.org | python3 -

# if you are using pyenv, add following config
# Poetry will then try to find the current python of your shell.
poetry config virtualenvs.prefer-active-python true

# orac uses river and river depends on rust,
# need to install rust compiler first (for unix based systems)
poetry run curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# install requirements, this will also create virtualenv
poetry install

# to see where dependencies have been installed run
poetry env info

# install pre-commit (this will use poetry virtual env)
poetry run pre-commit install

```

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
