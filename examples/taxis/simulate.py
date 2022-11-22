import argparse
import datetime as dt
import json
import time

import kafka
from river import datasets
from river import metrics
from river import stream


class colors:
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    ENDC = "\033[0m"


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("speed", type=int, nargs="?", default=1)
    args = parser.parse_args()

    def sleep(td: dt.timedelta):
        if td.seconds >= 0:
            time.sleep(td.seconds / args.speed)

    # Use the first trip's departure time as a reference time
    taxis = datasets.Taxis()
    now = next(iter(taxis))[0]["pickup_datetime"]
    predictions = {}

    # Empty topics for idempotency
    broker_admin = kafka.admin.KafkaAdminClient(bootstrap_servers=["localhost:9092"])
    for topic_name in ["taxi-departures", "taxi-arrivals"]:
        try:
            broker_admin.delete_topics([topic_name])
        except kafka.errors.UnknownTopicOrPartitionError:
            ...

    broker = kafka.KafkaProducer(
        bootstrap_servers=["localhost:9092"],
        key_serializer=str.encode,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    for trip_no, trip, duration in stream.simulate_qa(
        taxis,
        moment="pickup_datetime",
        delay=lambda _, duration: dt.timedelta(seconds=duration),
    ):
        trip_no = str(trip_no).zfill(len(str(taxis.n_samples)))

        # Taxi trip starts

        if duration is None:

            # Wait
            sleep(trip["pickup_datetime"] - now)
            now = trip["pickup_datetime"]

            broker.send(
                topic="taxi-departures",
                key=trip_no,
                value={**trip, "pickup_datetime": trip["pickup_datetime"].isoformat()},
            )

            print(colors.GREEN + f"#{trip_no} departs at {now}" + colors.ENDC)
            continue

        # Taxi trip ends

        # Wait
        arrival_time = trip["pickup_datetime"] + dt.timedelta(seconds=duration)
        sleep(arrival_time - now)
        now = arrival_time

        # Send the label
        print(trip_no, {"arrival_time": arrival_time.isoformat(), "duration": duration})
        broker.send(
            topic="taxi-arrivals",
            key=trip_no,
            value={"arrival_time": arrival_time.isoformat(), "duration": duration},
        )

        # Notify arrival and compare prediction against ground truth
        td = dt.timedelta(seconds=duration)
        print(colors.BLUE + f"#{trip_no} arrives at {now}, took {td}" + colors.ENDC)
