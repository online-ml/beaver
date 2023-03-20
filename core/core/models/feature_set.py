import fastapi
import sqlmodel as sqlm


class FeatureSet(sqlm.SQLModel, table=True):  # type: ignore[call-arg]
    __tablename__ = "feature_set"

    name: str = sqlm.Field(primary_key=True)
    query: str
    key_field: str
    ts_field: str

    project_name: str = sqlm.Field(default=None, foreign_key="project.name")
    project: "Project" = sqlm.Relationship(  # type: ignore[name-defined]
        sa_relationship_kwargs={"uselist": False}
    )

    experiments: list["Experiment"] = sqlm.Relationship(back_populates="feature_set")  # type: ignore[name-defined]
