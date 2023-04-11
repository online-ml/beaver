import enum


class Task(str, enum.Enum):
    binary_clf = "BINARY_CLASSIFICATION"
    regression = "REGRESSION"


class MessageBus(str, enum.Enum):
    kafka = "KAFKA"
    redpanda = "REDPANDA"
    sqlite = "SQLITE"
    pulsar = "PULSAR"


class StreamProcessor(str, enum.Enum):
    materialize = "MATERIALIZE"
    ksql = "KSQL"
    sqlite = "SQLITE"
    bytewax = "BYTEWAX"
    rising_wave = "RISING_WAVE"
    pinot = "PINOT"
    druid = "DRUID"


class JobRunner(str, enum.Enum):
    kafka = "CELERY"
    synchronous = "SYNCHRONOUS"
