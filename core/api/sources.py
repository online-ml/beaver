import fastapi
import kafka
import sqlmodel as sqlm

from api import db, infra, enums

router = fastapi.APIRouter()


class Source(sqlm.SQLModel, table=True):  # type: ignore[call-arg]
    id: int | None = sqlm.Field(default=None, primary_key=True)
    name: str
    protocol: enums.MessageBus
    url: str | None = None

    @property
    def message_bus(self):
        if self.protocol == enums.MessageBus.kafka:
            return kafka.KafkaConsumer(bootstrap_servers=[self.url])
        if self.protocol == enums.MessageBus.dummy:
            return infra.DummyMessageBus()
        raise NotImplementedError


@router.post("/")
def create_source(
    source: Source,
    session: sqlm.Session = fastapi.Depends(db.get_session),
):
    session.add(source)
    session.commit()
    session.refresh(source)
    return source


@router.get("/", response_model=list[Source])
def read_sources(
    offset: int = 0,
    limit: int = fastapi.Query(default=100, lte=100),
    session: sqlm.Session = fastapi.Depends(db.get_session),
):
    return session.exec(sqlm.select(Source).offset(offset).limit(limit)).all()


@router.get("/{source_id}")
def read_source(
    source_id: int,
    session: sqlm.Session = fastapi.Depends(db.get_session),
):
    source = session.get(Source, source_id)
    if not source:
        raise fastapi.HTTPException(status_code=404, detail="Source not found")
    return {**source.dict(), "topics": source.message_bus.topics}
