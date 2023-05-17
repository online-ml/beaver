from typing import Optional
import fastapi
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
    message_bus: "MessageBus" = sqlmodel.Relationship(back_populates="projects")  # type: ignore[name-defined]
    stream_processor: "StreamProcessor" = sqlmodel.Relationship(back_populates="projects")  # type: ignore[name-defined]
    job_runner: "JobRunner" = sqlmodel.Relationship(back_populates="projects")  # type: ignore[name-defined]
    target: Optional["Target"] = sqlmodel.Relationship(back_populates="project", sa_relationship_kwargs={"uselist": False})  # type: ignore[name-defined]
    feature_sets: list["FeatureSet"] = sqlmodel.Relationship(back_populates="project")  # type: ignore[name-defined]
    experiments: list["Experiment"] = sqlmodel.Relationship(back_populates="project")  # type: ignore[name-defined]

    @property
    def target_view_name(self):
        return f"{self.name}_target"

    @property
    def predictions_topic_name(self):
        return f"{self.name}_predictions"
