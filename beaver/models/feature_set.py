from __future__ import annotations

import sqlmodel

from .base import Base


class FeatureSet(Base, table=True):  # type: ignore[call-arg]
    __tablename__ = "feature_set"

    # Attributes
    name: str = sqlmodel.Field(primary_key=True)
    query: str
    key_field: str
    ts_field: str
    value_field: str
    project_name: str = sqlmodel.Field(default=None, foreign_key="project.name")

    # Relationships
    project: "Project" = sqlmodel.Relationship(  # noqa: F821, UP037
        sa_relationship_kwargs={"uselist": False}
    )
    experiments: list["Experiment"] = sqlmodel.Relationship(  # noqa: F821, UP037
        back_populates="feature_set"
    )
