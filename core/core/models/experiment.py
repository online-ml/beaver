import datetime as dt
import fastapi
import sqlmodel as sqlm


class Experiment(sqlm.SQLModel, table=True):  # type: ignore[call-arg]

    name: str = sqlm.Field(primary_key=True)
    model: bytes
    model_state: bytes | None = sqlm.Field(default=None)
    n_samples_trained_on: int = sqlm.Field(default=0)
    sync_seconds: int = sqlm.Field(default=20)
    last_ts_seen: dt.datetime | None = sqlm.Field(default=None)

    project_name: str = sqlm.Field(default=None, foreign_key="project.name")
    project: "Project" = sqlm.Relationship(  # type: ignore[name-defined]
        sa_relationship_kwargs={"uselist": False}
    )

    feature_set_name: str = sqlm.Field(foreign_key="feature_set.name")
    feature_set: "FeatureSet" = sqlm.Relationship(back_populates="experiments")  # type: ignore[name-defined]
