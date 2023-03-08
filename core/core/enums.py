import enum


class Task(str, enum.Enum):
    binary_clf = "BINARY_CLASSIFICATION"
    regression = "REGRESSION"


class MessageBus(str, enum.Enum):
    kafka = "KAFKA"
    redpanda = "REDPANDA"
    dummy = "DUMMY"


class StreamProcessor(str, enum.Enum):
    kafka = "MATERIALIZE"
    dummy = "DUMMY"


class TaskRunner(str, enum.Enum):
    kafka = "CELERY"
    dummy = "DUMMY"
