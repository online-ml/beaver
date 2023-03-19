import fastapi
import sqlmodel as sqlm

from core import db, models

router = fastapi.APIRouter()


@router.post("/", status_code=201)
def create_task_runner(
    task_runner: models.TaskRunner,
    session: sqlm.Session = fastapi.Depends(db.get_session),
):
    session.add(task_runner)
    session.commit()
    session.refresh(task_runner)
    return task_runner


@router.get("/", response_model=list[models.TaskRunner])
def read_task_runners(
    offset: int = 0,
    limit: int = fastapi.Query(default=100, lte=100),
    session: sqlm.Session = fastapi.Depends(db.get_session),
):
    return session.exec(
        sqlm.select(models.TaskRunner).offset(offset).limit(limit)
    ).all()


@router.get("/{name}")
def read_task_runner(
    name: str, session: sqlm.Session = fastapi.Depends(db.get_session)
):
    task_runner = session.get(models.TaskRunner, name)
    if not task_runner:
        raise fastapi.HTTPException(status_code=404, detail="Task runner not found")
    return task_runner
