import uuid
import sqlmodel

from .base import Base


class Job(Base, table=True):  # type: ignore[call-arg]
    # Attributes
    id: uuid.UUID = sqlmodel.Field(default_factory=uuid.uuid4, primary_key=True)
    n_predictions: int = sqlmodel.Field(default=0)
    n_learnings: int = sqlmodel.Field(default=0)
    experiment_name: str = sqlmodel.Field(foreign_key="experiment.name")

    # Relationships
    experiment: "Experiment" = sqlmodel.Relationship(  # noqa: F821
        back_populates="jobs"
    )
