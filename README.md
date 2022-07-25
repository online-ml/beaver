# 🦫 Beaver

<div align="center" >
  <img src="digital_art.png" width="33%" />
</div>

## Introduction

Beaver is a system to deploy and maintain machine learning models. It is designed from the ground up to support online machine learning models. But it also works if you want to do inference with batch models.

We want to provide a piece of software which takes care of the boring stuff, can be plugged into existing systems, and is fun to use.

More about Beaver [here](ABOUT.md).

## Installation

### Docker

The easiest way is to run the provided `docker-compose.yaml`.

```sh
git clone https://github.com/MaxHalford/beaver
cd beaver
docker-compose up
```

### Python package

You can also just install the `beaver` Python package.

```sh
pip install git+https://github.com/MaxHalford/beaver
```

Then it's up to you to handle the rest. The first thing to do is initialize a `Dam`.

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

Once it's running, the server can be interacted with via an HTTP client:

```py
import beaver
from river import linear_model

model = linear_model.LogisticRegression()

client = beaver.HTTPClient(host='http://127.0.0.1:3000')
client.models.upload('my_model', model)
```

## Examples

- [🚕 Taxis](examples/taxis)

## Deployment

### Docker

```sh
docker build -t beaver .
docker run -it -p 3000:3000 beaver
```

### Helm chart

Coming soon.

## Development

```sh
git clone https://github.com/online-ml/beaver
cd beaver
pip install poetry
poetry install
poetry shell
pytest
```

## License

Beaver is free and open-source software licensed under the [3-clause BSD license](LICENSE).
