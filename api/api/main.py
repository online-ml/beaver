import fastapi
from starlette.middleware.cors import CORSMiddleware

from .settings import settings
from api import db
from api import experiments
from api import feature_sets
from api import models
from api import processors
from api import runners
from api import sinks
from api import sources
from api import targets

app = fastapi.FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_PREFIX}/openapi.json"
)

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
router.include_router(experiments.router, prefix="/experiments", tags=["experiments"])
router.include_router(feature_sets.router, prefix="/features", tags=["features"])
router.include_router(models.router, prefix="/models", tags=["models"])
router.include_router(processors.router, prefix="/processors", tags=["processors"])
router.include_router(runners.router, prefix="/runners", tags=["runners"])
router.include_router(sinks.router, prefix="/sinks", tags=["sinks"])
router.include_router(sources.router, prefix="/sources", tags=["sources"])
router.include_router(targets.router, prefix="/targets", tags=["targets"])
app.include_router(router, prefix=settings.API_PREFIX)
