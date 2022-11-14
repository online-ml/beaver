import fastapi

from api import db
from api import processors
import psycopg
import sqlmodel as sqlm

router = fastapi.APIRouter()


class Features(sqlm.SQLModel, table=True):
    id: int | None = sqlm.Field(default=None, primary_key=True)
    name: str
    query: str
    key_field: str

    processor_id: int = sqlm.Field(foreign_key="processor.id")

    def create(self, session):
        processor = session.get(processors.Processor, self.processor_id)

        if not processor:
            raise fastapi.HTTPException(status_code=404, detail="Processor not found")

        conn = psycopg.connect(processor.url)
        conn.autocommit = True
        with conn.cursor() as cur:
            for q in self.query.split(";"):
                cur.execute(q)

        session.add(self)
        session.commit()
        session.refresh(self)

        return self


@router.post("/")
def create_features(features: Features):
    with db.session() as session:
        return features.create(session)


@router.get("/")
def read_features(offset: int = 0, limit: int = fastapi.Query(default=100, lte=100)):
    with db.session() as session:
        features = session.exec(
            sqlm.select(Features.id, Features.name, Features.key_field)
            .offset(offset)
            .limit(limit)
        ).all()
        return features


@router.get("/{features_id}")
def read_features(features_id: int):
    with db.session() as session:
        features = session.get(Features, features_id)
        if not features:
            raise fastapi.HTTPException(status_code=404, detail="Features not found")
        return features
