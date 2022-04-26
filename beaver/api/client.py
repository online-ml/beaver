from beaver.model import Model
import urllib.parse
import dill
import requests
import base64


def serialize_model(model):
    return base64.b64encode(dill.dumps(model)).decode("ascii")


class SDK:
    def __init__(self, host):
        self.host = host

    def _request(self, method, endpoint, **kwargs):
        r = requests.request(
            method=method, url=urllib.parse.urljoin(self.host, endpoint), **kwargs
        )
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            try:
                raise ValueError(r.json()) from e
            except requests.exceptions.JSONDecodeError:
                raise e
        return r


class ModelsSDK(SDK):
    def upload(self, name: str, model: Model):
        return self._request(
            "POST",
            "models",
            data={"name": name, "model_bytes": serialize_model(model)},
        )

    def delete(self, name: str):
        return self._request("DELETE", f"models/{name}")

    def list_names(self):
        return self._request("GET", "models").json()


class HTTPClient(SDK):
    def __init__(self, host):
        super().__init__(host=host)
        self.models = ModelsSDK(host=host)

    def predict(self, event, model_name, loop_id=None):
        payload = {"event": event}
        if loop_id is not None:
            payload["loop_id"] = loop_id
        return self._request("POST", f"predict/{model_name}", json=payload).json()

    def label(self, loop_id, label):
        self._request("POST", f"label/{loop_id}", json={"label": label})

    def train(self, model_name):
        self._request("POST", f"train/{model_name}")
