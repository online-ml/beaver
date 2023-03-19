import fastapi
import sqlmodel as sqlm

from core import infra as _infra, enums


class TaskRunner(sqlm.SQLModel, table=True):  # type: ignore[call-arg]
    __tablename__ = "task_runner"

    name: str = sqlm.Field(primary_key=True)
    protocol: enums.TaskRunner
    url: str | None = sqlm.Field(default=None)

    projects: list["Project"] = sqlm.Relationship(back_populates="task_runner")  # type: ignore[name-defined]

    @property
    def infra(self):
        if self.protocol == enums.TaskRunner.fastapi_background_tasks:
            from core.main import app

            return _infra.FastAPIBackgroundTasksRunner(app)
        raise NotImplementedError
