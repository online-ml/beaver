import base64
import functools
import fastapi
import sqlmodel as sqlm
import dill

from core import db, logic, models

router = fastapi.APIRouter()


@router.post("/", status_code=201)
def create_experiment(
    experiment: models.Experiment,
    session: sqlm.Session = fastapi.Depends(db.get_session),
):

    project = session.get(models.Project, experiment.project_name)
    if not project:
        raise fastapi.HTTPException(status_code=404, detail="Project not found")

    model_obj = dill.loads(base64.b64decode(experiment.model.decode("ascii")))
    experiment.model = dill.dumps(model_obj)

    # TODO: run model tasks

    session.add(experiment)
    session.commit()
    session.refresh(experiment)

    # Run inference in the background
    project.task_runner.infra.run(
        functools.partial(logic.do_inference, experiment.name)
    )

    return experiment
