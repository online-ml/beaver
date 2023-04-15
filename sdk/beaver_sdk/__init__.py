import functools
import json
import urllib.parse
import requests


class SDK:
    def __init__(self, host: str):
        self.host = host

    @functools.cache
    def session(self):
        s = requests.Session()
        return s

    def request(self, method, endpoint, as_json=True, session=None, **kwargs):
        r = (session or self.session()).request(
            method=method, url=urllib.parse.urljoin(self.host, endpoint), **kwargs
        )
        r.raise_for_status()
        return r.json() if as_json else r

    def get(self, endpoint, **kwargs):
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        return self.request("POST", endpoint, **kwargs)


class Instance:
    def __init__(self, host: str):
        self.host = host

    @property
    def project(self):
        """Access projects."""
        return ProjectFactory(self.host)

    def message_bus(self, name: str):
        return MessageBus(host=self.host, name=name)


class MessageBus(SDK):
    def __init__(self, host, name):
        super().__init__(host=urllib.parse.urljoin(host, f"/api/message-bus/{name}"))
        self.name = name

    def send(self, topic, key, value):
        self.post(
            "",
            json={"topic": topic, "key": str(key), "value": json.dumps(value)},
        )


class ProjectFactory(SDK):
    def __init__(self, host):
        super().__init__(host=urllib.parse.urljoin(host, "/api/project"))

    def create(
        self,
        name: str,
        task: str,
        message_bus_name: str,
        stream_processor_name: str,
        job_runner_name: str,
    ):
        """Create a project."""
        self.post(
            "",
            json={
                "name": name,
                "task": task,
                "message_bus_name": message_bus_name,
                "stream_processor_name": stream_processor_name,
                "job_runner_name": job_runner_name,
            },
        )
        return self(name)

    def list(self):
        """List existing projects."""
        return self.get("")

    def __call__(self, project_name: str):
        """Choose an existing project."""
        return Project(host=self.host, name=project_name)


class Project(SDK):
    def __init__(self, host, name):
        super().__init__(host="")
        self.name = name

    def get(self):
        return self.get(f"api/project/{self.name}")

    def define_target(
        self, query: str, key_field: str, ts_field: str, value_field: str
    ):
        return self.post(
            "api/target",
            json={
                "project_name": self.name,
                "query": query,
                "key_field": key_field,
                "ts_field": ts_field,
                "value_field": value_field,
            },
        )
