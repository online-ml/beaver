# Taxis

Simulating real traffic using the [*New York City Taxi Trip Duration* dataset](https://www.kaggle.com/c/nyc-taxi-trip-duration).

## Setup

```sh
pip install poetry
poetry install
poetry shell
pip install river
```

## Steps

The Beaver app is defined in `server.py`. It gives access to a [FastAPI](https://fastapi.tiangolo.com/) server which you can start from the terminal:

```sh
uvicorn server:app.http_server --port 3000

# Alternatively, you can do this if you're developping
uvicorn server:app.http_server --port 3000 --reload --reload-dir ../../
```

Then we upload a River model from a second terminal. The model is serialized with [dill](https://github.com/uqfoundation/dill) and the bytes are send over HTTP.

```sh
python upload_model.py
```

Now we can simulate traffic, in exactly the same order and with the same delays as what would have happened in production. We'll apply a x15 speed-up.

```sh
python simulate.py 15
```

You can periodically retrain the model in a third terminal, say, every 10 seconds:

```sh
python train.py 10
```

We can check the predictive performance from a Python interpreter.

```py
import pandas as pd
import sqlite3

with sqlite3.connect('taxis.sqlite') as con:
    print(pd.read_sql_table('metrics', con))
```
