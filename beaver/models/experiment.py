import datetime as dt
import dill
import sqlmodel

from .base import Base


class Experiment(Base, table=True):  # type: ignore[call-arg]
    # Attributes
    name: str = sqlmodel.Field(primary_key=True)
    model: bytes
    can_learn: bool = sqlmodel.Field(default=False)
    model_state: bytes | None = sqlmodel.Field(default=None)
    sync_seconds: int = sqlmodel.Field(default=20)
    start_from_top: bool = sqlmodel.Field(default=False)
    last_sample_ts: dt.datetime | None = sqlmodel.Field(default=None)
    project_name: str = sqlmodel.Field(default=None, foreign_key="project.name")
    feature_set_name: str = sqlmodel.Field(foreign_key="feature_set.name")

    # Relationships
    project: "Project" = sqlmodel.Relationship(  # noqa: F821
        sa_relationship_kwargs={"uselist": False}
    )
    feature_set: "FeatureSet" = sqlmodel.Relationship(  # noqa: F821
        back_populates="experiments"
    )
    jobs: list["Job"] = sqlmodel.Relationship(  # noqa: F821
        back_populates="experiment", sa_relationship_kwargs={"cascade": "delete"}
    )

    def get_model(self):
        return dill.loads(self.model_state)

    def set_model(self, model):
        self.model_state = dill.dumps(model)
