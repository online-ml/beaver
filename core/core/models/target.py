import fastapi
import sqlmodel

from core import enums

from .base import Base


class Target(Base, table=True):  # type: ignore[call-arg]

    # Attributes
    project_name: str = sqlmodel.Field(foreign_key="project.name", primary_key=True)
    query: str
    key_field: str
    ts_field: str
    target_field: str

    # Relationships
    project: "Project" = sqlmodel.Relationship(  # type: ignore[name-defined]
        back_populates="target", sa_relationship_kwargs={"uselist": False}
    )
