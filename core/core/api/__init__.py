import fastapi

from . import message_bus, project, stream_processor, target

router = fastapi.APIRouter()
router.include_router(message_bus.router, prefix="/message_bus", tags=["message_bus"])
router.include_router(project.router, prefix="/project", tags=["project"])
router.include_router(
    stream_processor.router, prefix="/stream_processor", tags=["stream_processor"]
)
router.include_router(target.router, prefix="/target", tags=["target"])
