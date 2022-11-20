import enum


class TaskEnum(str, enum.Enum):
    binary_clf = "BINARY_CLASSIFICATION"
    regression = "REGRESSION"
