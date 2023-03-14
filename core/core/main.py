import contextlib
import os

import sqlmodel as sqlm
import fastapi
from starlette.middleware.cors import CORSMiddleware

from .settings import settings
from core import api, db


app = fastapi.FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_PREFIX}/openapi.json"
)


@app.on_event("startup")
def on_startup():
    db.create_db_and_tables()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://ui",
        "http://ui:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router, prefix=settings.API_PREFIX)
