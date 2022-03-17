from __future__ import annotations
import datetime as dt
import dataclasses
import dataclasses_json
import uuid


@dataclasses.dataclass
class Ingredient(dataclasses_json.DataClassJsonMixin):
    created_at: dt.datetime = dataclasses.field(
        default_factory=dt.datetime.now, init=False
    )


@dataclasses.dataclass
class Event(Ingredient):
    data: dict
    loop_id: str | uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)


@dataclasses.dataclass
class Features(Ingredient):
    data: dict
    model_name: str
    loop_id: str | uuid.UUID


@dataclasses.dataclass
class Prediction(Ingredient):
    data: dict[str | bool, float] | int | float
    model_name: str
    loop_id: str | uuid.UUID


@dataclasses.dataclass
class Label(Ingredient):
    data: str | bool | int | float
    loop_id: str | uuid.UUID
