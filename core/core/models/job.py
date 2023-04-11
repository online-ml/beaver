import uuid
import sqlmodel


class Job(sqlmodel.SQLModel, table=True):  # type: ignore[call-arg]
    id: uuid.UUID = sqlmodel.Field(default_factory=uuid.uuid4, primary_key=True)
    n_predictions: int = sqlmodel.Field(default=0)
    n_learnings: int = sqlmodel.Field(default=0)

    experiment_name: str = sqlmodel.Field(foreign_key="experiment.name")
    experiment: "Experiment" = sqlmodel.Relationship(back_populates="jobs")  # type: ignore[name-defined]
