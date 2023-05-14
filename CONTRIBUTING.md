# Contribution guidelines

## Setup

Regardless of how you develop, you need a Python environment to run pre-commit hooks.

```sh
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

# Beaver uses River and River depends on Rust,
# need to install Rust compiler first (for UNIX based systems)
poetry run curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# install requirements, this will also create virtualenv
poetry install
poetry install --with sdk

# to see where dependencies have been installed run
poetry env info

# install pre-commit (this will use poetry virtual env)
poetry run pre-commit install

```

### 🐍 Developping with Python

Once that's done, you just have to activate the environment.

```sh
poetry shell
```

Now you can run the server.

```sh
uvicorn beaver.main:app --port 8000 --reload --reload-dir beaver
```

And also run unit tests.

```sh
pytest
```

And also run the web interface.

```sh
export BEAVER_HOST=http://localhost
streamlit run ui/Home.py
```


### 🐳 Developping with Docker

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

## Handbook

### Contributing infrastructure

#### Message bus

- Add attribute to `enums/MessageBus`
- Add class to `infra/message_bus.py`
- Add `if` condition to `models/MessageBus.infra`

#### Stream processor

- Add attribute to `enums.MessageBus`
- Add class to `infra/stream_processor.py`
- Add `if` condition to `models/MessageBus.infra`
- Add iteration and performance logic to `core/logic.py`

#### Job runner

- Add attribute to `enums/JobRunner`
- Add class to `infra/job_runner.py`
- Add `if` condition to `models/JobRunner.infra`
