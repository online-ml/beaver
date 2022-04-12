from __future__ import annotations
import abc
import contextlib
import shelve
import pathlib
from typing import Optional
import uuid

import beaver


class ModelStore(abc.ABC):
    def build(self):
        ...

    @abc.abstractmethod
    def store(self, envelope: ModelEnvelope):
        ...

    @abc.abstractmethod
    def list_names(self):
        ...

    @abc.abstractmethod
    def get(self, name: str) -> Optional[ModelEnvelope]:
        ...

    @abc.abstractmethod
    def delete(self, name: str):
        ...

    def clear(self):
        raise NotImplementedError


class ShelveModelStore(ModelStore):
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
            db[envelope.name] = envelope

    def list_names(self):
        with self.db() as db:
            return list(db.keys())

    def get(self, name):
        with self.db() as db:
            return db.get(name)

    def delete(self, name):
        with self.db() as db:
            db.pop(name, None)

    def clear(self):
        pathlib.Path(str(self.path) + ".db").unlink()
