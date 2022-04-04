import beaver
from river import linear_model, preprocessing


client = beaver.HTTPClient(host="http://127.0.0.1:8000")

model = preprocessing.StandardScaler() | linear_model.LinearRegression()

print(client.upload_model("wooha", model).status_code)
print(client.list_models())
