import fastapi
import sqlmodel

from core import infra as _infra, enums

from .base import Base


class JobRunner(Base, table=True):  # type: ignore[call-arg]
    __tablename__ = "job_runner"

    # Attributes
    name: str = sqlmodel.Field(primary_key=True)
    protocol: enums.JobRunner
    url: str | None = sqlmodel.Field(default=None)

    # Relationships
    projects: list["Project"] = sqlmodel.Relationship(back_populates="job_runner")  # type: ignore[name-defined]

    @property
    def infra(self):
        if self.protocol == enums.JobRunner.synchronous:
            return _infra.SynchronousJobRunner()
        raise NotImplementedError
