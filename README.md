# 🦫 Beaver

## Introduction

Beaver is a system to deploy and maintain machine learning models. In particular, it caters to online models, which includes inference as well learning on streaming data.

Beaver is the latest of an ongoing trial and error process. The compromise we've settled on is to answer 80% of needs without worrying too much about scale, performance, security, etc. We want to provide a piece of software which takes care of (most of) the boring stuff, is pluggable, and is fun to use.

## Design principles

Much of Beaver's design can be traced back to some of Max Halford's [talks](https://maxhalford.github.io/links/#talks), with [this one](https://www.youtube.com/watch?v=nzFTmJnIakk&list=PLIU25-FciwNaz5PqWPiHmPCMOFYoEsJ8c&index=5) in particular.

The central object is the `Dam`. It holds all the components necessary to perform online machine learning. For instance, a `data_store` which will store predictions, features, and labels has to be chosen, while `model_store` has to be picked to store models. This is where Beaver is generic: you can use whatever model and data store you want, as long as they satisfy the necessary interfaces.

A strong design principle is that Beaver is technology agnostic. If you want to store data in Redis, or use MLFlow as a model store, then so be it. The only strong decision is that Beaver is written in Python.

Once instantiated, the `Dam` is supposed to be run on a server. There are then multiple ways to interact with it. The most common way would be to start an HTTP server, and interact with said server from a client. That is one way to use Beaver. But you can also directly use the `Dam` you instantiated, for instance if you don't need to have a client/server separation. This might be the case if you're deploying a model on an embedded device with no internet connection.

## Installation

### Docker

The easiest way is to run the provided `docker-compose.yaml`.

```sh
git clone https://github.com/MaxHalford/beaver
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
)
dam.build()
```

The `build` method makes sure each component is ready to be used. Assuming the above code is in a file named `server.py`, you may then start an HTTP server by leveraging FastAPI:

```py
uvicorn server:dam.http_server --port 3000
```

## Usage

The server can then be interacted with via an HTTP client:

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
pip install poetry
poetry install
poetry shell
pytest
```

## License

Beaver is free and open-source software licensed under the [3-clause BSD license](LICENSE).
