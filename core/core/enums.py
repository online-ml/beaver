import enum


class Task(str, enum.Enum):
    binary_clf = "BINARY_CLASSIFICATION"
    regression = "REGRESSION"


class MessageBus(str, enum.Enum):
    kafka = "KAFKA"
    redpanda = "REDPANDA"
    sqlite = "SQLITE"


class StreamProcessor(str, enum.Enum):
    materialize = "MATERIALIZE"
    ksql = "KSQL"
    sqlite = "SQLITE"


class TaskRunner(str, enum.Enum):
    kafka = "CELERY"
    fastapi_background_tasks = "FASTAPI_BACKGROUND_TASKS"
