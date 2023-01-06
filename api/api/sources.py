import fastapi
import kafka
import sqlmodel as sqlm

from api import db

router = fastapi.APIRouter()


class Source(sqlm.SQLModel, table=True):  # type: ignore[call-arg]
    id: int | None = sqlm.Field(default=None, primary_key=True)
    name: str
    protocol: str
    url: str


@router.post("/")
def create_source(source: Source):
    with db.session() as session:
        session.add(source)
        session.commit()
        session.refresh(source)
        return source


@router.get("/", response_model=list[Source])
def read_sources(offset: int = 0, limit: int = fastapi.Query(default=100, lte=100)):
    with db.session() as session:
        return session.exec(sqlm.select(Source).offset(offset).limit(limit)).all()


@router.get("/{source_id}")
def read_source(source_id: int):
    with db.session() as session:
        source = session.get(Source, source_id)
        consumer = kafka.KafkaConsumer(bootstrap_servers=[source.url])
        if not source:
            raise fastapi.HTTPException(status_code=404, detail="Source not found")
        return {**source.dict(), "topics": consumer.topics}
