import enum


class AutoName(enum.Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class Regime(AutoName):
    ASAP = enum.auto()
    MANUAL = enum.auto()
