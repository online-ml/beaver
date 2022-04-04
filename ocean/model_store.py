from __future__ import annotations
import abc
import contextlib
import shelve
import pathlib
import dataclasses
import dataclasses_json
from typing import Optional
import uuid

import ocean


@dataclasses.dataclass
class ModelEnvelope(dataclasses_json.DataClassJsonMixin):
    name: str
    sku: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)
    parent_sku: Optional[uuid.UUID] = None
    model_bytes: Optional[bytes] = None


class ModelStore(abc.ABC):
    def prepare(self):
        ...

    @abc.abstractmethod
    def store(self, envelope: ModelEnvelope):
        ...

    @abc.abstractmethod
    def get_all(self):
        ...

    @abc.abstractmethod
    def get(self, sku: uuid.UUID) -> ModelEnvelope:
        ...

    def clear(self):
        raise NotImplementedError


class ShelveModelStore(ModelStore):
    """

    >>> import ocean
    >>> import uuid

    >>> model_store = ocean.model_store.ShelveModelStore("model_jar")

    >>> envelope = ocean.ModelEnvelope("foo")
    >>> model_store.store(envelope)
    >>> model_store.get(envelope.sku).name
    'foo'

    >>> model_store.clear()
    >>> try:
    ...     model_store.get(envelope.sku)
    ... except KeyError:
    ...     print("Key doesn't exist")
    Key doesn't exist

    """

    def __init__(self, path):
        self.path = pathlib.Path(path)

    @contextlib.contextmanager
    def db(self, *args, **kwds):
        db = shelve.open(str(self.path))
        try:
            yield db
        finally:
            db.close()

    def store(self, envelope):
        with self.db() as db:
            db[str(envelope.sku)] = envelope

    def get_all(self):
        with self.db() as db:
            return [self.get(sku) for sku in db.keys()]

    def get(self, sku):
        with self.db() as db:
            return db[str(sku)]

    def clear(self):
        pathlib.Path(str(self.path) + ".db").unlink()
