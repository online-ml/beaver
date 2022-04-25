from river import datasets
import beaver

dataset = datasets.Taxis()

client = beaver.HTTPClient(host="http://127.0.0.1:3000")

for x, y in dataset.take(3):
    print(x, y)
    x["pickup_datetime"] = x["pickup_datetime"].isoformat()
    prediction = client.predict(event=x, model_name="Linear regression")
    loop_id = prediction["loop_id"]
    client.label(label=y, loop_id=loop_id)
