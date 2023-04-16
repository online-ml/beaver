import base64
import dill
import functools
import json
import urllib.parse
import requests
import river.base


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

    def put(self, endpoint, **kwargs):
        return self.request("PUT", endpoint, **kwargs)


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

    def state(self):
        return self.get(f"api/project/{self.name}").json()

    def set_target(self, query: str, key_field: str, ts_field: str, value_field: str):
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

    @property
    def feature_set(self):
        return FeatureSetFactory(host=self.host, project_name=self.name)

    @property
    def target(self):
        return TargetFactory(host=self.host, project_name=self.name)

    @property
    def experiment(self):
        return ExperimentFactory(host=self.host, project_name=self.name)


class TargetFactory(SDK):
    def __init__(self, host, project_name: str):
        super().__init__(host=urllib.parse.urljoin(host, "/api/target"))
        self.project_name = project_name

    def set(self, query: str, key_field: str, ts_field: str, value_field: str):
        """Define a project's target."""
        self.post(
            "",
            json={
                "project_name": self.project_name,
                "query": query,
                "key_field": key_field,
                "ts_field": ts_field,
                "value_field": value_field,
            },
        )


class FeatureSetFactory(SDK):
    def __init__(self, host, project_name: str):
        super().__init__(host=urllib.parse.urljoin(host, "/api/feature-set"))
        self.project_name = project_name

    def create(
        self, name: str, query: str, key_field: str, ts_field: str, value_field: str
    ):
        """Create a feature set."""
        self.post(
            "",
            json={
                "name": name,
                "project_name": self.project_name,
                "query": query,
                "key_field": key_field,
                "ts_field": ts_field,
                "value_field": value_field,
            },
        )


class ExperimentFactory(SDK):
    def __init__(self, host, project_name: str):
        super().__init__(host=urllib.parse.urljoin(host, "/api/experiment"))
        self.project_name = project_name

    def create(
        self,
        name: str,
        feature_set_name: str,
        model,
        start_from_top: bool = False,
    ):
        """Create an experiment."""

        # Add method aliases
        if isinstance(model, river.base.Estimator):
            model.learn = model.learn_one
            model.predict = model.predict_one

        self.post(
            "",
            json={
                "name": name,
                "project_name": self.project_name,
                "feature_set_name": feature_set_name,
                "model": base64.b64encode(dill.dumps(model)).decode("ascii"),
                "start_from_top": start_from_top,
            },
        )

        return self(name)

    def __call__(self, experiment_name: str):
        """Choose an existing experiment."""
        return Experiment(host=self.host, name=experiment_name)


class Experiment(SDK):
    def __init__(self, host, name):
        super().__init__(host="")
        self.name = name

    def start(self):
        self.put(f"api/experiment/{self.name}/start")
