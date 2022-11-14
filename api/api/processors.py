import fastapi

from api import db
import sqlmodel as sqlm

router = fastapi.APIRouter()


class Processor(sqlm.SQLModel, table=True):
    id: int | None = sqlm.Field(default=None, primary_key=True)
    name: str
    protocol: str
    url: str


@router.post("/")
def create_processor(processor: Processor):
    with db.session() as session:
        session.add(processor)
        session.commit()
        session.refresh(processor)
        return processor


@router.get("/", response_model=list[Processor])
def read_processors(offset: int = 0, limit: int = fastapi.Query(default=100, lte=100)):
    with db.session() as session:
        processors = session.exec(
            sqlm.select(Processor).offset(offset).limit(limit)
        ).all()
        return processors


@router.get("/{processor_id}")
def read_processor(processor_id: int):
    with db.session() as session:
        processor = session.get(Processor, processor_id)
        if not processor:
            raise fastapi.HTTPException(status_code=404, detail="Processor not found")
        return processor
