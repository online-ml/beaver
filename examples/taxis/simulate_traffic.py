from river import datasets
import beaver

dataset = datasets.Taxis()

client = beaver.HTTPClient(host="http://127.0.0.1:8000")

for x, y in dataset.take(3):
    print(x, y)
    x["pickup_datetime"] = x["pickup_datetime"].isoformat()
    print(client.predict(event=x, model_name="Linear regression"))
