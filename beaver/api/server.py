import functools
import dill
from fastapi import Depends, File, Form, FastAPI
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


class PredictEvent(pydantic.BaseModel):
    event: dict


@api.post("/predict/{model_name}")
async def predict(
    model_name: str,
    predict_event: PredictEvent,
    settings: Settings = Depends(get_settings),
):
    # TODO: the prediction is not JSON serializable because of created_at which is a datetime
    return settings.app.predict(event=predict_event.event, model_name=model_name)


# @api.post("/models/leader")
# async def set_leader():
#     ...


# @api.post("/label/")
# async def label():
#     ...
