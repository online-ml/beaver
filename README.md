<h1>🦫 Beaver — MLOps for (online) machine learning</h1>

- [Introduction](#introduction)
- [Installation](#installation)
  - [Docker](#docker)
  - [Python package](#python-package)
- [Usage](#usage)
- [Examples](#examples)
- [Development](#development)
- [License](#license)

## Introduction

<div align="center" >
  <img src="digital_art.png" width="33%" align="right" />
</div>

Beaver is a system to deploy and maintain machine learning models. It is **designed for online machine learning models**. But it **also works with batch models** if all you want to do is inference and performance monitoring.

We want to provide a piece of software which takes care of the boring stuff, can be plugged into existing systems, and is fun to use.

More about Beaver [here](ABOUT.md).

## Installation

### Docker

The easiest way is to run the provided `docker-compose.yaml`.

```sh
git clone https://github.com/online-ml/beaver
cd beaver
docker-compose up
```

### Python package

You can also just install the `beaver` Python package.

```sh
pip install git+https://github.com/online-ml/beaver
```

Then it's up to you to handle the rest. The first thing to do is create a `Dam`:

```py
import beaver

dam = beaver.Dam(
    model_store=beaver.model_store.ShelveModelStore('~Downloads'),
    data_store=beaver.data_store.SQLDataStore('sqlite:///db.sqlite'),
    training_regimes=[beaver.training.Regime.ASAP]
)
dam.build()
```

The `build` method makes sure each component is ready to be used. Assuming the above code is in a file named `server.py`, you may then start an HTTP server by leveraging FastAPI:

```py
uvicorn server:dam.http_server --port 3000
```

## Usage

Once it's running, you can talk to the server over HTTP:

```py
import beaver
from river import linear_model

model = linear_model.LogisticRegression()

client = beaver.HTTPClient(host='http://127.0.0.1:3000')
client.models.upload('my_model', model)
```

## Examples

- [🚕 Taxis](examples/taxis)

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

## License

Beaver is free and open-source software licensed under the [3-clause BSD license](LICENSE).
