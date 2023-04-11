import typing
import fastapi


class JobRunner(typing.Protocol):
    def run(self, task):
        ...


class SynchronousJobRunner:
    def run(self, task):
        task()
