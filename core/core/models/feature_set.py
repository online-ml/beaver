import fastapi
import sqlmodel as sqlm


class FeatureSet(sqlm.SQLModel, table=True):  # type: ignore[call-arg]
    __tablename__ = "feature_set"

    name: str = sqlm.Field(primary_key=True)
    query: str
    key_field: str

    project_name: str
