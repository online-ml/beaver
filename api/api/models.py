import enum
import dill
import fastapi

from api import db
from api import tasks
import sqlmodel as sqlm

router = fastapi.APIRouter()


class Model(sqlm.SQLModel, table=True):
    id: int | None = sqlm.Field(default=None, primary_key=True)
    name: str
    task: tasks.TaskEnum
    content: bytes

    experiments: list["Experiment"] = sqlm.Relationship(back_populates="model")


@router.post("/")
def create_model(model: Model):
    with db.session() as session:
        session.add(model)
        session.commit()
        session.refresh(model)
        return model


@router.get("/")
def read_models(offset: int = 0, limit: int = fastapi.Query(default=100, lte=100)):
    with db.session() as session:
        return session.exec(
            sqlm.select(Model.id, Model.name).offset(offset).limit(limit)
        ).all()


@router.get("/{model_id}")
def read_model(model_id: int):
    with db.session() as session:
        model = session.get(Model, model_id)
        if not model:
            raise fastapi.HTTPException(status_code=404, detail="Model not found")
        model_obj = dill.loads(model.content)
        return {
            "name": model.name,
            "task": model.task,
            "class": f"{model_obj.__module__}.{model_obj.__class__.__name__}",
            "repr": repr(model_obj),
        }
