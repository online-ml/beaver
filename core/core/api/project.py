import fastapi
import sqlmodel as sqlm

from core import db, models

router = fastapi.APIRouter()


@router.post("/", status_code=201)
def create_project(
    project: models.Project, session: sqlm.Session = fastapi.Depends(db.get_session)
):
    processor = session.get(models.StreamProcessor, project.stream_processor_name)
    if not processor:
        raise fastapi.HTTPException(
            status_code=404, detail="Stream processor not found"
        )

    session.add(project)
    session.commit()
    session.refresh(project)

    # Create performance view for monitoring experiments
    project.stream_processor.infra.create_performance_view(project_name=project.name)

    return project


@router.get("/")
def read_projects(
    offset: int = 0,
    limit: int = fastapi.Query(default=100, lte=100),
    session: sqlm.Session = fastapi.Depends(db.get_session),
):
    return session.exec(sqlm.select(models.Project).offset(offset).limit(limit)).all()


@router.get("/{name}")
def read_project(
    name: str,
    session: sqlm.Session = fastapi.Depends(db.get_session),
):
    project = session.get(models.Project, name)
    performance = project.stream_processor.infra.get_performance_view(
        project_name=project.name
    )
    if not project:
        raise fastapi.HTTPException(status_code=404, detail="Project not found")
    return {**project.dict(), "performance": performance}
