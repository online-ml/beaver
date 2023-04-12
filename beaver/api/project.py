import fastapi
import sqlmodel as sqlm
from beaver import db, logic, models

router = fastapi.APIRouter()


@router.post("/", status_code=201)
def create_project(
    project: models.Project, session: sqlm.Session = fastapi.Depends(db.get_session)
):

    if not session.get(models.StreamProcessor, project.stream_processor_name):
        raise fastapi.HTTPException(
            status_code=404,
            detail=f"Stream processor '{project.stream_processor_name}' not found",
        )

    if not session.get(models.MessageBus, project.message_bus_name):
        raise fastapi.HTTPException(
            status_code=404,
            detail=f"Message bus '{project.message_bus_name}' not found",
        )

    if not session.get(models.JobRunner, project.job_runner_name):
        raise fastapi.HTTPException(
            status_code=404,
            detail=f"Job runner '{project.job_runner_name}' not found",
        )

    project.save(session)

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
    """Return a project's current state."""
    project = session.get(models.Project, name)
    if not project:
        raise fastapi.HTTPException(status_code=404, detail="Project not found")
    return {
        **project.dict(),
        "experiments": logic.monitor_experiments(project_name=project.name),
    }
