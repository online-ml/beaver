import fastapi

from api import db
from api import processors
import sqlmodel as sqlm

router = fastapi.APIRouter()


class FeatureSet(sqlm.SQLModel, table=True):
    __tablename__ = "feature_set"

    id: int | None = sqlm.Field(default=None, primary_key=True)
    name: str
    query: str
    key_field: str

    processor_id: int = sqlm.Field(foreign_key="processor.id")
    processor: processors.Processor = sqlm.Relationship(back_populates="feature_sets")
    experiments: list["Experiment"] = sqlm.Relationship(back_populates="feature_set")

    def create(self, session):
        processor = session.get(processors.Processor, self.processor_id)
        if not processor:
            raise fastapi.HTTPException(status_code=404, detail="Processor not found")
        processor.execute(self.query)

        session.add(self)
        session.commit()
        session.refresh(self)

        return self


@router.post("/")
def create_feature_set(feature_set: FeatureSet):
    with db.session() as session:
        return feature_set.create(session)


@router.get("/")
def read_feature_set(offset: int = 0, limit: int = fastapi.Query(default=100, lte=100)):
    with db.session() as session:
        return session.exec(
            sqlm.select(FeatureSet.id, FeatureSet.name, FeatureSet.key_field)
            .offset(offset)
            .limit(limit)
        ).all()


@router.get("/{feature_set_id}")
def read_feature_set(feature_set_id: int):
    with db.session() as session:
        feature_set = session.get(FeatureSet, feature_set_id)
        if not feature_set:
            raise fastapi.HTTPException(status_code=404, detail="FeatureSet not found")
        return feature_set
