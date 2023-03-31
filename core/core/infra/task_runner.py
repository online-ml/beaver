import typing
import fastapi


class TaskRunner(typing.Protocol):
    def run(self, task):
        ...


class SynchronousTaskRunner:
    def run(self, task):
        task()
