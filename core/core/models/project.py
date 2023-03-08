import fastapi
import sqlmodel as sqlm

from api import db, targets, sinks

router = fastapi.APIRouter()


class Project(sqlm.SQLModel, table=True):  # type: ignore[call-arg]
    id: int | None = sqlm.Field(default=None, primary_key=True)
    name: str
    target_id: int = sqlm.Field(foreign_key="target.id")
    # target: targets.Target = sqlm.Relationship(back_populates="projects")
    sink_id: int = sqlm.Field(foreign_key="sink.id")
    # sink: sinks.Sink = sqlm.Relationship(back_populates="projects")

    experiments: list["Experiment"] = sqlm.Relationship(back_populates="project")  # type: ignore[name-defined] # noqa
