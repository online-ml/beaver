import fastapi
import sqlmodel as sqlm

from core import db, models

router = fastapi.APIRouter()


@router.post("/", status_code=201)
def create_feature_set(
    feature_set: models.FeatureSet,
    session: sqlm.Session = fastapi.Depends(db.get_session),
):

    project = session.get(models.Project, feature_set.project_name)
    if not project:
        raise fastapi.HTTPException(status_code=404, detail="Project not found")

    # Check if the query is valid
    project.stream_processor.infra.create_view(
        name=feature_set.name, query=feature_set.query
    )

    feature_set.save(session)

    return feature_set


@router.get("/")
def read_feature_sets(
    offset: int = 0,
    limit: int = fastapi.Query(default=100, lte=100),
    session: sqlm.Session = fastapi.Depends(db.get_session),
):
    return session.exec(
        sqlm.select(models.FeatureSet).offset(offset).limit(limit)
    ).all()


@router.get("/{name}")  # type: ignore[no-redef]
def read_feature_set(
    name: str, session: sqlm.Session = fastapi.Depends(db.get_session)
):  # noqa
    feature_set = session.get(models.FeatureSet, name)
    if not feature_set:
        raise fastapi.HTTPException(status_code=404, detail="Feature set not found")
    return feature_set
