import fastapi
import sqlmodel as sqlm

from core import enums

router = fastapi.APIRouter()


class Target(sqlm.SQLModel, table=True):  # type: ignore[call-arg]
    id: int | None = sqlm.Field(default=None, primary_key=True)
    query: str
    key_field: str
    target_field: str

    project_name: str
    project: "Project" = sqlm.Relationship(  # type: ignore[name-defined]
        sa_relationship_kwargs={"uselist": False}, back_populates="target"
    )
