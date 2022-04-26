import datetime as dt
import dataclasses
import dataclasses_json
import uuid
from typing import Optional, Union

from beaver import types


@dataclasses.dataclass
class LoopPart(dataclasses_json.DataClassJsonMixin):
    created_at: dt.datetime = dataclasses.field(
        default_factory=dt.datetime.now, init=False
    )


@dataclasses.dataclass
class Event(LoopPart):
    content: dict
    loop_id: Optional[str] = None

    def __post_init__(self):
        if self.loop_id is None:
            self.loop_id = str(uuid.uuid4())


@dataclasses.dataclass
class Features(LoopPart):
    content: dict
    model_name: str
    loop_id: str


@dataclasses.dataclass
class Prediction(LoopPart):
    content: Union[dict[types.ClfLabel, float], types.RegLabel]
    model_name: str
    loop_id: str


@dataclasses.dataclass
class Label(LoopPart):
    content: types.Label
    loop_id: str
