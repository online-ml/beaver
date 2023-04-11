import uuid
import sqlmodel as sqlm


class Job(sqlm.SQLModel, table=True):  # type: ignore[call-arg]
    id: uuid.UUID = sqlm.Field(default_factory=uuid.uuid4, primary_key=True)
    n_predictions: int = sqlm.Field(default=0)
    n_learnings: int = sqlm.Field(default=0)

    experiment_name: str = sqlm.Field(foreign_key="experiment.name")
    experiment: "Experiment" = sqlm.Relationship(back_populates="jobs")  # type: ignore[name-defined]
