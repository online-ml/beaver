import fastapi

from . import (
    experiment,
    feature_set,
    message_bus,
    project,
    stream_processor,
    target,
    task_runner,
)

router = fastapi.APIRouter()
router.include_router(feature_set.router, prefix="/feature-set", tags=["feature-set"])
router.include_router(message_bus.router, prefix="/message-bus", tags=["message-bus"])
router.include_router(project.router, prefix="/project", tags=["project"])
router.include_router(
    stream_processor.router, prefix="/stream-processor", tags=["stream-processor"]
)
router.include_router(target.router, prefix="/target", tags=["target"])
router.include_router(task_runner.router, prefix="/task-runner", tags=["task-runner"])
router.include_router(experiment.router, prefix="/experiment", tags=["experiment"])
