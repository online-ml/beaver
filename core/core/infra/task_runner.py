import typing
import fastapi


class TaskRunner(typing.Protocol):
    def run(self, task):
        ...


class FastAPIBackgroundTasksRunner:
    def __init__(self, app: fastapi.FastAPI):
        self.app = app

    def run(self, task):
        self.app.background_tasks.add_task(task)
