from ocean.model import Model
import urllib.parse
import dill
import requests
import base64


class HTTPClient:
    def __init__(self, host):
        self.host = host

    def _request(self, method, endpoint, **kwargs):
        return requests.request(
            method=method, url=urllib.parse.urljoin(self.host, endpoint), **kwargs
        )

    def upload_model(self, name: str, model: Model):
        return self._request(
            "POST",
            "models",
            data={"name": name, "model_bytes": dill.dumps(model)},
        )

    def list_models(self):
        return self._request("GET", "models").json()
