import functools
from fastapi import Depends, File, Form, FastAPI
import pydantic
import ocean

api = FastAPI()


class Settings(pydantic.BaseSettings):
    ocean_app: ocean.App = None


@functools.lru_cache()
def get_settings():
    return Settings()


@api.post("/models/")
async def upload_model(
    name: str = Form(...),
    model_bytes: bytes = File(...),
    settings: Settings = Depends(get_settings),
):
    envelope = ocean.model_store.ModelEnvelope(name=name, model_bytes=model_bytes)
    settings.ocean_app.model_store.store(envelope)


class ModelView(pydantic.BaseModel):
    name: str
    sku: str


@api.get("/models/")
async def list_models(settings: Settings = Depends(get_settings)):
    return [
        ModelView(name=envelope.name, sku=str(envelope.sku))
        for envelope in settings.ocean_app.model_store.get_all()
    ]


# @api.post("/models/leader")
# async def set_leader():
#     ...


# @api.get("/predict/")
# async def predict():
#     ...


# @api.post("/label/")
# async def label():
#     ...
