import fastapi
from . import message_bus
from . import stream_processor

router = fastapi.APIRouter()
router.include_router(message_bus.router, prefix="/message_bus", tags=["message_bus"])
router.include_router(
    stream_processor.router, prefix="/stream_processor", tags=["stream_processor"]
)
