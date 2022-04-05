from typing import Optional
import dataclasses
import dataclasses_json


@dataclasses.dataclass
class ModelEnvelope(dataclasses_json.DataClassJsonMixin):
    name: str
    is_featurizer: bool
    is_learner: bool
    model_bytes: Optional[bytes] = None
    is_active: bool = True
