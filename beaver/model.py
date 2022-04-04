from __future__ import annotations
from typing import Protocol

from beaver import types


class Model(Protocol):
    def predict(self, features: dict):
        ...


class Featurizer(Protocol):
    def featurize(self, event: dict):
        ...


class Learner(Protocol):
    def learn(self, features: dict, label: types.Label):
        ...
