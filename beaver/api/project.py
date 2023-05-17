import fastapi
import sqlmodel as sqlm

from beaver import db, enums, logic, models

router = fastapi.APIRouter()


@router.post("/", status_code=201)
def create_project(
    project: models.Project, session: sqlm.Session = fastapi.Depends(db.get_session)
):

    if not (
        stream_processor := session.get(
            models.StreamProcessor, project.stream_processor_name
        )
    ):
        raise fastapi.HTTPException(
            status_code=404,
            detail=f"Stream processor '{project.stream_processor_name}' not found",
        )

    if not (message_bus := session.get(models.MessageBus, project.message_bus_name)):
        raise fastapi.HTTPException(
            status_code=404,
            detail=f"Message bus '{project.message_bus_name}' not found",
        )

    if not session.get(models.JobRunner, project.job_runner_name):
        raise fastapi.HTTPException(
            status_code=404,
            detail=f"Job runner '{project.job_runner_name}' not found",
        )

    # Bootstrap necessary views
    if stream_processor.protocol == enums.StreamProcessor.materialize:
        if message_bus.protocol not in {
            enums.MessageBus.kafka,
            enums.MessageBus.redpanda,
        }:
            raise fastapi.HTTPException(
                status_code=400,
                detail="Materialize only supports Kafka and Redpanda message buses",
            )
        stream_processor.infra.execute(
            f"DROP VIEW IF EXISTS {project.predictions_topic_name}"
        )
        stream_processor.infra.execute(
            f"DROP SOURCE IF EXISTS {project.predictions_topic_name}_src"
        )
        stream_processor.infra.execute(
            f"""
        CREATE MATERIALIZED SOURCE {project.predictions_topic_name}_src
        FROM KAFKA BROKER '{message_bus.url}' TOPIC '{project.predictions_topic_name}'
            KEY FORMAT TEXT
            VALUE FORMAT BYTES
            INCLUDE KEY AS key, TIMESTAMP AS ts;
        """
        )

        stream_processor.infra.execute(
            f"""
        CREATE VIEW {project.predictions_topic_name} AS (
            SELECT
                key,
                ts,
                CAST(CONVERT_FROM(data, 'utf8') AS JSONB) AS prediction
            FROM {project.predictions_topic_name}_src
        )
        """
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
    with_experiments: bool = False,
):
    """Return a project's current state."""
    project = session.get(models.Project, name)
    if not project:
        raise fastapi.HTTPException(status_code=404, detail="Project not found")
    state = project.dict()
    if with_experiments:
        state["experiments"] = logic.monitor_experiments(project_name=project.name)
    return state


@router.delete("/{name}", status_code=204)
def delete_project(
    name: str,
    session: sqlm.Session = fastapi.Depends(db.get_session),
):
    project = session.get(models.Project, name)
    if not project:
        raise fastapi.HTTPException(status_code=404, detail="Project not found")
    project.delete(session)
