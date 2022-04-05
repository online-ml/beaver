from __future__ import annotations
from typing import Protocol, runtime_checkable

from beaver import types


@runtime_checkable
class Model(Protocol):
    def predict(self, features: dict):
        ...


@runtime_checkable
class Featurizer(Protocol):
    def featurize(self, event: dict):
        ...


@runtime_checkable
class Learner(Protocol):
    def learn(self, features: dict, label: types.Label):
        ...
