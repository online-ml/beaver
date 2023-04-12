import fastapi
import sqlmodel as sqlm
from core import db, models

router = fastapi.APIRouter()


@router.post("/", status_code=201)
def create_stream_processor(
    stream_processor: models.StreamProcessor,
    session: sqlm.Session = fastapi.Depends(db.get_session),
):
    stream_processor.save(session)
    return stream_processor


@router.get("/", response_model=list[models.StreamProcessor])
def read_stream_processors(
    offset: int = 0,
    limit: int = fastapi.Query(default=100, lte=100),
    session: sqlm.Session = fastapi.Depends(db.get_session),
):
    return session.exec(
        sqlm.select(models.StreamProcessor).offset(offset).limit(limit)
    ).all()


@router.get("/{name}")
def read_stream_processor(
    name: str,
    session: sqlm.Session = fastapi.Depends(db.get_session),
):
    stream_processor = session.get(models.StreamProcessor, name)
    if not stream_processor:
        raise fastapi.HTTPException(
            status_code=404, detail="Stream processor not found"
        )
    return stream_processor
