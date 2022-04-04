import datetime as dt
import dataclasses
import dataclasses_json
import uuid
from typing import Union

from beaver import types


@dataclasses.dataclass
class Ingredient(dataclasses_json.DataClassJsonMixin):
    created_at: dt.datetime = dataclasses.field(
        default_factory=dt.datetime.now, init=False
    )


@dataclasses.dataclass
class Event(Ingredient):
    content: dict
    loop_id: Union[str, uuid.UUID] = dataclasses.field(default_factory=uuid.uuid4)


@dataclasses.dataclass
class Features(Ingredient):
    content: dict
    model_name: str
    loop_id: Union[str, uuid.UUID]


@dataclasses.dataclass
class Prediction(Ingredient):
    content: Union[dict[types.ClfLabel, float], types.RegLabel]
    model_name: str
    loop_id: Union[str, uuid.UUID]


@dataclasses.dataclass
class Label(Ingredient):
    content: types.Label
    loop_id: Union[str, uuid.UUID]
