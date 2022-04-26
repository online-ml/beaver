import functools
import dill
from typing import Optional
from fastapi import Depends, File, Form, FastAPI
from fastapi.encoders import jsonable_encoder
import pydantic
import beaver
import base64

api = FastAPI()


class Settings(pydantic.BaseSettings):
    app: beaver.App = None


@functools.lru_cache()
def get_settings():
    return Settings()


def deserialize_model(model_bytes):
    return dill.loads(base64.b64decode(model_bytes.encode("ascii")))


@api.post("/models/")
async def post_model(
    name: str = Form(...),
    model_bytes: str = File(...),
    settings: Settings = Depends(get_settings),
):
    model = deserialize_model(model_bytes)
    settings.app.store_model(name, model)


@api.delete("/models/{name}")
async def delete_model(name: str, settings: Settings = Depends(get_settings)):
    settings.app.model_store.delete(name)


@api.get("/models/")
async def get_models(settings: Settings = Depends(get_settings)):
    return settings.app.model_store.list_names()


class PredictIn(pydantic.BaseModel):
    event: dict
    loop_id: Optional[str] = None


@api.post("/predict/{model_name}")
async def predict(
    model_name: str,
    payload: PredictIn,
    settings: Settings = Depends(get_settings),
):
    prediction = settings.app.make_prediction(
        event=payload.event, model_name=model_name, loop_id=payload.loop_id
    )
    return jsonable_encoder(prediction)


class LabelIn(pydantic.BaseModel):
    label: beaver.types.Label


@api.post("/label/{loop_id}")
async def label(
    loop_id: str,
    payload: LabelIn,
    settings: Settings = Depends(get_settings),
):
    settings.app.store_label(loop_id=loop_id, label=payload.label)


@api.post("/train/{model_name}")
async def train(
    model_name: str,
    settings: Settings = Depends(get_settings),
):
    n_rows = settings.app.train_model(model_name=model_name)
    return {"n_rows": n_rows}
