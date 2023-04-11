from typing import Optional
import fastapi
import sqlmodel as sqlm

from core import enums

router = fastapi.APIRouter()


class Project(sqlm.SQLModel, table=True):  # type: ignore[call-arg]
    name: str = sqlm.Field(default=None, primary_key=True)
    task: enums.Task

    message_bus_name: str = sqlm.Field(foreign_key="message_bus.name")
    message_bus: "MessageBus" = sqlm.Relationship(back_populates="projects")  # type: ignore[name-defined]

    stream_processor_name: str = sqlm.Field(foreign_key="stream_processor.name")
    stream_processor: "StreamProcessor" = sqlm.Relationship(back_populates="projects")  # type: ignore[name-defined]

    job_runner_name: str = sqlm.Field(foreign_key="job_runner.name")
    job_runner: "JobRunner" = sqlm.Relationship(back_populates="projects")  # type: ignore[name-defined]

    target_id: int | None = sqlm.Field(default=None, foreign_key="target.id")
    target: Optional["Target"] = sqlm.Relationship(back_populates="project")  # type: ignore[name-defined]

    feature_sets: list["FeatureSet"] = sqlm.Relationship(back_populates="project")  # type: ignore[name-defined]
    experiments: list["Experiment"] = sqlm.Relationship(back_populates="project")  # type: ignore[name-defined]

    @property
    def target_view_name(self):
        return f"{self.name}_target"

    @property
    def predictions_topic_name(self):
        return f"{self.name}_predictions"
