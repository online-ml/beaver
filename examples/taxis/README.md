# Taxis

Simulating real traffic using the [*New York City Taxi Trip Duration* dataset](https://www.kaggle.com/c/nyc-taxi-trip-duration).

## General idea

This proccedure helps understand how beaver can be used to predict trip durations of taxis using an event dataset consisting of pickup date-times, pickup coordinates, arrival coordinates, etc.

* The procedure here is to create an empty model using the river library
* Serialize the model using dill
* Upload the model using the beaver http client --> you could also do this using the HTTP API directly (see localhost:3000/docs for more details)
* Then start receiving trip data in a simulation and make predictions for trip duration

During simulation you should see the error decreasing with time, which can be visualized in the output messages as in:

`
... a taxi starts a trip with id 000014
#0000014 departs at 2016-01-01 00:04:57
... times goes by
... eventually the trip ends
#0000014 arrives at 2016-01-01 00:08:37, took 0:03:40, predicted 0:08:41
`

so for the trip 000014 we can see an error of more then 200% in this case

## Setup

First of all you need a running instance of Beaver. For instance, you can to the root of this repo and start an instance in the background:

```sh
(cd ... && docker-compose up -d && docker exec -it app /bin/bash)
# now interactive docker shell starts in /app directory, then do this:
cd examples/taxis
```

You have to install the Beaver client to interact with the Beaver server:

```sh
pip install platformdirs
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
