from __future__ import annotations

import typing

import sqlmodel

from beaver import enums

from .base import Base


class Project(Base, table=True):  # type: ignore[call-arg]
    # Attributes
    name: str = sqlmodel.Field(default=None, primary_key=True)
    task: enums.Task
    message_bus_name: str = sqlmodel.Field(foreign_key="message_bus.name")
    stream_processor_name: str = sqlmodel.Field(foreign_key="stream_processor.name")
    job_runner_name: str = sqlmodel.Field(foreign_key="job_runner.name")

    # Relationships
    message_bus: "MessageBus" = sqlmodel.Relationship(  # noqa: F821, UP037
        back_populates="projects"
    )
    stream_processor: "StreamProcessor" = sqlmodel.Relationship(  # noqa: F821, UP037
        back_populates="projects"
    )
    job_runner: "JobRunner" = sqlmodel.Relationship(back_populates="projects")  # noqa: F821, UP037
    target: typing.Union["Target", None] = sqlmodel.Relationship(  # noqa: F821, UP037, UP007
        back_populates="project", sa_relationship_kwargs={"uselist": False}
    )
    feature_sets: list["FeatureSet"] = sqlmodel.Relationship(  # noqa: F821, UP037
        back_populates="project"
    )
    experiments: list["Experiment"] = sqlmodel.Relationship(  # noqa: F821, UP037
        back_populates="project"
    )

    @property
    def target_view_name(self):
        return f"{self.name}_target"

    @property
    def predictions_topic_name(self):
        return f"{self.name}_predictions"
