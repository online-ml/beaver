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


class Instance:
    def __init__(self, host: str):
        self.host = host

    @property
    def project(self):
        return Project(self.host)


class Project(SDK):
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
        self.request(
            "POST",
            "",
            json={
                "name": name,
                "task": task,
                "message_bus_name": message_bus_name,
                "stream_processor_name": stream_processor_name,
                "job_runner_name": job_runner_name,
            },
        )

    def list(self):
        return self.request("GET", "")
