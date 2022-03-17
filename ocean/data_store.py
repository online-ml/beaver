from __future__ import annotations
import abc
import contextlib
import uuid
import pathlib
import shelve

from ocean import ingredients


class DataStore(abc.ABC):
    def prepare(self):
        ...

    @abc.abstractmethod
    def store_ingredient(
        self, ingredient_name: str, ingredient: ingredients.Ingredient
    ):
        ...

    def store_event(self, event: ingredients.Event):
        return self.store_ingredient("event", event)

    def store_features(self, features: ingredients.Features):
        return self.store_ingredient("features", features)

    def store_prediction(self, prediction: ingredients.Prediction):
        return self.store_ingredient("prediction", prediction)

    def store_label(self, label: ingredients.Label):
        return self.store_ingredient("label", label)

    @abc.abstractmethod
    def get_ingredient(self, ingredient_name: str, loop_id: str | uuid.UUID):
        ...

    def get_event(self, loop_id: str | uuid.UUID):
        return self.get_ingredient("event", loop_id)

    def get_features(self, loop_id: str | uuid.UUID):
        return self.get_ingredient("features", loop_id)

    def get_prediction(self, loop_id: str | uuid.UUID):
        return self.get_ingredient("prediction", loop_id)

    def get_label(self, loop_id: str | uuid.UUID):
        return self.get_ingredient("label", loop_id)

    def clear(self):
        raise NotImplementedError


class ShelveDataStore(DataStore):
    """

    >>> import ocean

    >>> data_store = ocean.data_store.ShelveDataStore("data_jar")

    >>> event = ocean.Event({"foo": 42})
    >>> data_store.store_event(event)
    >>> data_store.get_event(event.loop_id).content
    {'foo': 42}

    >>> data_store.clear()
    >>> try:
    ...     data_store.get_event(event.loop_id)
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

    def store_ingredient(self, ingredient_name, ingredient):
        with self.db() as db:
            db[f"{ingredient_name}/{ingredient.loop_id}"] = ingredient

    def get_ingredient(self, ingredient_name, loop_id):
        with self.db() as db:
            return db[f"{ingredient_name}/{loop_id}"]

    def clear(self):
        pathlib.Path(str(self.path) + ".db").unlink()
