import fastapi
import sqlmodel as sqlm

from core import db, models

router = fastapi.APIRouter()


@router.post("/", status_code=201)
def create_experiment(
    experiment: models.Experiment,
    session: sqlm.Session = fastapi.Depends(db.get_session),
):

    project = session.get(models.Project, experiment.project.name)
    if not project:
        raise fastapi.HTTPException(status_code=404, detail="Project not found")

    # model_obj = dill.loads(base64.b64decode(model.content.decode("ascii")))
    # model.content = dill.dumps(model_obj)

    # TODO: run model tasks

    session.add(experiment)
    session.commit()
    session.refresh(experiment)

    return experiment
