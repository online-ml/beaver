import enum


class Flavor(enum.Enum):
    CLF_BINARY = "binary classification"
    CLF_MULTI = "multi-class classification"
    REG = "regression"
    ANOMALY_DETECTION = "anomaly detection"
