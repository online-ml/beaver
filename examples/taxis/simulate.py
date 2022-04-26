import argparse
import datetime as dt
import json
import time

import beaver
from river import datasets
from river import metrics
from river import stream


class colors:
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    ENDC = "\033[0m"


if __name__ == "__main__":

    client = beaver.HTTPClient(host="http://127.0.0.1:3000")

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

            # Get a prediction
            predictions[trip_no] = client.predict(
                event={
                    **trip,
                    "pickup_datetime": trip["pickup_datetime"].isoformat(),
                },
                model_name="Linear regression",
                loop_id=trip_no,
            )

            print(colors.GREEN + f"#{trip_no} departs at {now}" + colors.ENDC)
            continue

        # Taxi trip ends

        # Wait
        arrival_time = trip["pickup_datetime"] + dt.timedelta(seconds=duration)
        sleep(arrival_time - now)
        now = arrival_time

        # Send the label
        client.label(loop_id=trip_no, label=duration)

        # Notify arrival and compare prediction against ground truth
        yt = dt.timedelta(seconds=duration)
        yp = dt.timedelta(seconds=round(predictions.pop(trip_no)["content"]))
        print(
            colors.BLUE
            + f"#{trip_no} arrives at {now}, took {yt}, predicted {yp}"
            + colors.ENDC
        )
