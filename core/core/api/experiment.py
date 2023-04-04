import base64
import datetime as dt
import functools
import typing

import dill
import fastapi
import pydantic
import sqlmodel as sqlm

from core import db, logic, models

router = fastapi.APIRouter()


@typing.runtime_checkable
class Model(typing.Protocol):
    def predict(self, x: dict) -> typing.Any:
        ...

    def learn(self, x: dict, y: typing.Any) -> None:
        ...


class ExperimentOut(pydantic.BaseModel):
    name: str
    n_samples_trained_on: int
    sync_seconds: str | None
    last_ts_seen: dt.datetime | None
    project_name: str
    feature_set_name: str


@router.post("/", status_code=201)
def create_experiment(
    experiment: models.Experiment,
    session: sqlm.Session = fastapi.Depends(db.get_session),
) -> ExperimentOut:

    project = session.get(models.Project, experiment.project_name)
    if not project:
        raise fastapi.HTTPException(status_code=404, detail="Project not found")

    model_obj = dill.loads(base64.b64decode(experiment.model.decode("ascii")))
    if not isinstance(model_obj, Model):
        raise fastapi.HTTPException(
            status_code=400, detail="Model does not implement the expected protocol"
        )
    experiment.model_state = dill.dumps(model_obj)

    session.add(experiment)
    session.commit()
    session.refresh(experiment)

    # Run inference in the background
    project.task_runner.infra.run(
        functools.partial(logic.do_inference, experiment.name)
    )

    return experiment
