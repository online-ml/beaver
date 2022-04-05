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
        r.raise_for_status()
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


class HTTPClient:
    def __init__(self, host):
        self.models = ModelsSDK(host=host)
