import contextlib
import os

import sqlmodel as sqlm
import fastapi
from starlette.middleware.cors import CORSMiddleware

from .settings import settings

from api import (  # isort:skip
    db,
    experiments,
    feature_sets,
    projects,
    models,
    processors,
    runners,
    sinks,
    sources,
    targets,
)


# DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///database.db")

# connect_args = {"check_same_thread": False}
# engine = sqlm.create_engine(DATABASE_URL, echo=True, connect_args=connect_args)


# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)


# def get_session():
#     with Session(engine) as session:
#         yield session


# @app.on_event("startup")
# def on_startup():
#     create_db_and_tables()


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

router = fastapi.APIRouter()
router.include_router(experiments.router, prefix="/projects", tags=["projects"])
router.include_router(experiments.router, prefix="/experiments", tags=["experiments"])
router.include_router(feature_sets.router, prefix="/features", tags=["features"])
router.include_router(models.router, prefix="/models", tags=["models"])
router.include_router(processors.router, prefix="/processors", tags=["processors"])
router.include_router(runners.router, prefix="/runners", tags=["runners"])
router.include_router(sinks.router, prefix="/sinks", tags=["sinks"])
router.include_router(sources.router, prefix="/sources", tags=["sources"])
router.include_router(targets.router, prefix="/targets", tags=["targets"])
app.include_router(router, prefix=settings.API_PREFIX)
