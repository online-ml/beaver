import beaver
from river import linear_model, preprocessing


client = beaver.HTTPClient(host="http://127.0.0.1:8000")

models = {
    "Linear regression": preprocessing.StandardScaler()
    | linear_model.LinearRegression()
}

for name in client.models.list_names():
    print(f"Deleting {name}")
    client.models.delete(name)

for name, model in models.items():
    print(f"Uploading {name}")
    client.models.upload(name, model)
