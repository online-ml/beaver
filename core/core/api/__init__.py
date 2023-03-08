import fastapi
from . import message_bus

router = fastapi.APIRouter()
router.include_router(message_bus.router, prefix="/message_bus", tags=["message_bus"])
