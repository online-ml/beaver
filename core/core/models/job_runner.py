import fastapi
import sqlmodel as sqlm

from core import infra as _infra, enums


class JobRunner(sqlm.SQLModel, table=True):  # type: ignore[call-arg]
    __tablename__ = "job_runner"

    name: str = sqlm.Field(primary_key=True)
    protocol: enums.JobRunner
    url: str | None = sqlm.Field(default=None)

    projects: list["Project"] = sqlm.Relationship(back_populates="job_runner")  # type: ignore[name-defined]

    @property
    def infra(self):
        if self.protocol == enums.JobRunner.synchronous:
            return _infra.SynchronousJobRunner()
        raise NotImplementedError
