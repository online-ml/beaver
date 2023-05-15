from __future__ import annotations

import sqlmodel

from beaver import enums
from beaver import infra as _infra

from .base import Base


class JobRunner(Base, table=True):  # type: ignore[call-arg]
    __tablename__ = "job_runner"

    # Attributes
    name: str = sqlmodel.Field(primary_key=True)
    protocol: enums.JobRunner
    url: str | None = sqlmodel.Field(default=None)

    # Relationships
    projects: list["Project"] = sqlmodel.Relationship(  # noqa: F821, UP037
        back_populates="job_runner"
    )

    @property
    def infra(self):
        if self.protocol == enums.JobRunner.synchronous:
            return _infra.SynchronousJobRunner()
        if self.protocol == enums.JobRunner.celery:
            return _infra.CeleryJobRunner(self.url)
        if self.protocol == enums.JobRunner.rq:
            return _infra.RQJobRunner(self.url)
        raise NotImplementedError
