import functools
import urllib.parse
import requests


class SDK:
    def __init__(self, host: str):
        self.host = host

    @functools.cache
    def session(self):
        s = requests.Session()
        return s

    def request(self, method, endpoint, session=None, **kwargs):
        r = (session or self.session()).request(
            method=method, url=urllib.parse.urljoin(self.host, endpoint), **kwargs
        )
        r.raise_for_status()
        return r


class Instance(SDK):
    def __init__(self, host: str):
        super().__init__(host)

    def create_message_bus(self, name: str, protocol: str, url: str | None = None):
        self.request(
            "POST",
            "/api/message-bus",
            json={"name": name, "protocol": protocol, "url": url},
        )


class Project(SDK):
    def __init__(self, name: str):
        self.name = name

    def create(
        self,
        task: str,
        message_bus_name: str,
        stream_processor_name: str,
        job_runner_name: str,
    ):
        self.request(
            "POST",
            "/api/project",
            json={
                "name": self.name,
                "task": "BINARY_CLASSIFICATION",
                "message_bus_name": "test_mb",
                "stream_processor_name": "test_sp",
                "job_runner_name": "test_tr",
            },
        )
        assert response.status_code == 201
