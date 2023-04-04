import fastapi
import sqlmodel as sqlm

from core import db, models

router = fastapi.APIRouter()


@router.post("/", status_code=201)
def create_target(
    target: models.Target, session: sqlm.Session = fastapi.Depends(db.get_session)
):
    project = session.get(models.Project, target.project_name)
    if not project:
        raise fastapi.HTTPException(status_code=404, detail="Project not found")

    # Check if the query is valid
    project.stream_processor.infra.create_view(
        name=f"{project.name}_target", query=target.query
    )

    session.add(target)
    session.commit()
    session.refresh(target)

    return target


@router.get("/")
def read_targets(
    offset: int = 0,
    limit: int = fastapi.Query(default=100, lte=100),
    session: sqlm.Session = fastapi.Depends(db.get_session),
):
    return session.exec(sqlm.select(models.Target).offset(offset).limit(limit)).all()


@router.get("/{name}")
def read_target(
    name: str,
    session: sqlm.Session = fastapi.Depends(db.get_session),
):
    target = session.get(models.Target, name)
    if not target:
        raise fastapi.HTTPException(status_code=404, detail="Target not found")
    return target
