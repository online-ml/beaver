import fastapi
from starlette.middleware.cors import CORSMiddleware

from .settings import settings
from api import db
from api import sources

app = fastapi.FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_PREFIX}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

router = fastapi.APIRouter()
router.include_router(sources.router, prefix="/sources", tags=["sources"])
app.include_router(router, prefix=settings.API_PREFIX)


@app.get("/ping")
def pong():
    return {"ping": "ponç"}
