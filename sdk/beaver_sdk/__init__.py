import base64
import dill
import functools
import json
import urllib.parse
import requests
import river.base
import sklearn.base
import types


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

    @property
    def message_bus(self):
        return MessageBusFactory(host=self.host)

    @property
    def stream_processor(self):
        return StreamProcessorFactory(host=self.host)

    @property
    def job_runner(self):
        return JobRunnerFactory(host=self.host)


class MessageBusFactory(SDK):
    def create(self, name: str, protocol: str, url: str):
        """Create a message bus."""
        self.post(
            "/api/message-bus/",
            json={"name": name, "protocol": protocol, "url": url},
        )
        return self(name)

    def list(self):
        """List existing message buses."""
        return self.get("/api/message-bus/")

    def __call__(self, message_bus_name: str):
        """Choose an existing message bus."""
        return MessageBus(host=self.host, name=message_bus_name)


class MessageBus(SDK):
    def __init__(self, host, name):
        super().__init__(host)
        self.name = name

    def send(self, topic, key, value):
        self.post(
            f"/api/message-bus/{self.name}",
            json={"topic": topic, "key": str(key), "value": json.dumps(value)},
        )


class StreamProcessorFactory(SDK):
    def create(self, name: str, protocol: str, url: str):
        """Create a stream processor."""
        self.post(
            "/api/stream-processor/",
            json={"name": name, "protocol": protocol, "url": url},
        )
        return self(name)

    def list(self):
        """List existing stream processors."""
        return self.get("/api/stream-processor/")

    def __call__(self, stream_processor_name: str):
        """Choose an existing stream processor."""
        return StreamProcessor(host=self.host, name=stream_processor_name)


class StreamProcessor(SDK):
    def __init__(self, host, name):
        super().__init__(host)
        self.name = name


class JobRunnerFactory(SDK):
    def create(self, name: str, protocol: str, url: str | None = None):
        """Create a job runner."""
        self.post(
            "/api/job-runner/",
            json={"name": name, "protocol": protocol, "url": url},
        )
        return self(name)

    def list(self):
        """List existing job runners."""
        return self.get("/api/job-runner/")

    def __call__(self, job_runner_name: str):
        """Choose an existing job runner."""
        return JobRunner(host=self.host, name=job_runner_name)


class JobRunner(SDK):
    def __init__(self, host, name):
        super().__init__(host)
        self.name = name


class ProjectFactory(SDK):
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
            "/api/project/",
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
        return self.get("/api/project/")

    def __call__(self, project_name: str):
        """Choose an existing project."""
        return Project(host=self.host, name=project_name)


class Project(SDK):
    def __init__(self, host, name):
        super().__init__(host=host)
        self.name = name

    def state(self):
        return self.get(f"/api/project/{self.name}")

    def set_target(self, query: str, key_field: str, ts_field: str, value_field: str):
        return self.post(
            "/api/target/",
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
        super().__init__(host)
        self.project_name = project_name

    def set(self, query: str, key_field: str, ts_field: str, value_field: str):
        """Define a project's target."""
        self.post(
            "/api/target/",
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
        super().__init__(host)
        self.project_name = project_name

    def create(
        self, name: str, query: str, key_field: str, ts_field: str, value_field: str
    ):
        """Create a feature set."""
        self.post(
            "/api/feature-set/",
            json={
                "name": name,
                "project_name": self.project_name,
                "query": query,
                "key_field": key_field,
                "ts_field": ts_field,
                "value_field": value_field,
            },
        )


def sklearn_predict(model, x):
    return model._predict([list(x.values())])[0]


class ExperimentFactory(SDK):
    def __init__(self, host, project_name: str):
        super().__init__(host)
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
        elif isinstance(model, sklearn.base.BaseEstimator):
            model._predict = model.predict
            model.predict = types.MethodType(sklearn_predict, model)

        self.post(
            "/api/experiment/",
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
        super().__init__(host)
        self.name = name

    def start(self):
        self.put(f"/api/experiment/{self.name}/start")
