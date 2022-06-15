# Taxis

Simulating real traffic using the [*New York City Taxi Trip Duration* dataset](https://www.kaggle.com/c/nyc-taxi-trip-duration).

## Setup

First of all you need a running instance of Beaver. For instance, you can to the root of this repo and start an instance in the background:

```sh
(cd ... && docker-compose up -d)
```

You have to install the Beaver client to interact with the Beaver server:

```sh
poetry install
poetry shell
```

Then there are a few extra Python requirements you have to install for this example.

```sh
pip install -r requirements.txt
```

## Steps

Let's first upload a [River](https://github.com/online-ml/river) model. The model is serialized with [dill](https://github.com/uqfoundation/dill) and the bytes are sent over HTTP.

```sh
python upload_model.py
```

Now we can simulate traffic. The order is the same as what happened in production. This is because we know the departure and arrival times of each taxi trip, and can thus reproduce the exact same timeline. We'll apply a x15 speed-up to make things more exciting.

```sh
python simulate.py 15
```

You can periodically retrain the model in another, say, every 10 seconds:

```sh
python train.py 10
```
