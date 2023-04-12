import datetime as dt
import dill
import fastapi
import sqlmodel

from .base import Base


class Experiment(Base, table=True):  # type: ignore[call-arg]

    # Attributes
    name: str = sqlmodel.Field(primary_key=True)
    model: bytes
    model_state: bytes | None = sqlmodel.Field(default=None)
    sync_seconds: int = sqlmodel.Field(default=20)
    start_from_top: bool = sqlmodel.Field(default=False)
    last_sample_ts: dt.datetime | None = sqlmodel.Field(default=None)
    project_name: str = sqlmodel.Field(default=None, foreign_key="project.name")
    feature_set_name: str = sqlmodel.Field(foreign_key="feature_set.name")

    # Relationships
    project: "Project" = sqlmodel.Relationship(  # type: ignore[name-defined]
        sa_relationship_kwargs={"uselist": False}
    )
    feature_set: "FeatureSet" = sqlmodel.Relationship(back_populates="experiments")  # type: ignore[name-defined]
    jobs: list["Job"] = sqlmodel.Relationship(back_populates="experiment")  # type: ignore[name-defined]

    def get_model(self):
        return dill.loads(self.model_state)

    def set_model(self, model):
        self.model_state = dill.dumps(model)
