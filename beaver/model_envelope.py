from typing import Optional
import datetime as dt
import dataclasses
import dataclasses_json


@dataclasses.dataclass
class ModelEnvelope(dataclasses_json.DataClassJsonMixin):
    name: str
    is_featurizer: bool
    is_learner: bool
    model_bytes: Optional[bytes] = None
    is_active: bool = True
    last_label_created_at: Optional[dt.datetime] = None
