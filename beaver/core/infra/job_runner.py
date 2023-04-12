import typing
import fastapi


class JobRunner(typing.Protocol):
    def start(self, task: typing.Callable) -> str:
        ...

    def stop(self, task_id: str) -> None:
        ...


class SynchronousJobRunner:
    def start(self, task):
        task()

    def stop(self, task_id):
        pass


class CeleryJobRunner:
    def __init__(self, broker_url):
        self.celery_app = celery.Celery("beaver", broker=broker_url)

    def start(self, task):
        return self.celery_app.send_task(task).id

    def stop(self, task_id):
        self.celery_app.control.revoke(task_id)
