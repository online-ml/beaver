import argparse
import datetime as dt
import time
import beaver

client = beaver.HTTPClient(host="http://127.0.0.1:3000")

parser = argparse.ArgumentParser()
parser.add_argument("every_seconds", type=int, nargs="?", default=30)
args = parser.parse_args()

while True:
    time.sleep(args.every_seconds)
    client.train(model_name="Linear regression")
    print(f"Training completed at {dt.datetime.now()}")
