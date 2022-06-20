import beaver
from river import compose
from river import linear_model
from river import preprocessing


client = beaver.HTTPClient(host="http://127.0.0.1:3000")


def parse(trip):
    import datetime as dt

    if not isinstance(trip["pickup_datetime"], dt.datetime):
        trip["pickup_datetime"] = dt.datetime.fromisoformat(trip["pickup_datetime"])

    return trip


def distances(trip):
    import math

    lat_dist = trip["dropoff_latitude"] - trip["pickup_latitude"]
    lon_dist = trip["dropoff_longitude"] - trip["pickup_longitude"]
    return {
        "manhattan_distance": abs(lat_dist) + abs(lon_dist),
        "euclidean_distance": math.sqrt(lat_dist**2 + lon_dist**2),
    }


def datetime_info(trip):
    import calendar

    day_no = trip["pickup_datetime"].weekday()
    return {
        "hour": trip["pickup_datetime"].hour,
        **{day: i == day_no for i, day in enumerate(calendar.day_name)},
    }


models = {
    "Linear regression": (
        compose.FuncTransformer(parse)
        | (compose.FuncTransformer(distances) + compose.FuncTransformer(datetime_info))
        | preprocessing.StandardScaler()
        | linear_model.LinearRegression()
    )
}

for name in client.models.list_names():
    print(f"Deleting '{name}'")
    client.models.delete(name)

for name, model in models.items():
    print(f"Uploading '{name}'")
    model.predict = model.predict_one
    model.learn = model.learn_one
    client.models.upload(name, model)
