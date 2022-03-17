from __future__ import annotations
import abc
import contextlib
import uuid
import pathlib
import shelve

import ocean


class DataStore(abc.ABC):
    def prepare(self):
        ...

    @abc.abstractmethod
    def store(self, kind: str, ingredient: ocean.Ingredient):
        ...

    def store_event(self, event: ocean.Event):
        return self.store("event", event)

    def store_features(self, features: ocean.Features):
        return self.store("features", features)

    def store_prediction(self, prediction: ocean.Prediction):
        return self.store("prediction", prediction)

    def store_label(self, label: ocean.Label):
        return self.store("label", label)

    @abc.abstractmethod
    def get(self, kind: str, loop_id: str | uuid.UUID):
        ...

    def get_event(self, loop_id: str | uuid.UUID):
        return self.get("event", loop_id)

    def get_features(self, loop_id: str | uuid.UUID):
        return self.get("features", loop_id)

    def get_prediction(self, loop_id: str | uuid.UUID):
        return self.get("prediction", loop_id)

    def get_label(self, loop_id: str | uuid.UUID):
        return self.get("label", loop_id)

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

    def store(self, kind, ingredient):
        with self.db() as db:
            db[f"{kind}/{ingredient.loop_id}"] = ingredient

    def get(self, kind, loop_id):
        with self.db() as db:
            return db[f"{kind}/{loop_id}"]

    def clear(self):
        pathlib.Path(str(self.path) + ".db").unlink()


import sqlalchemy as sqla
import sqlalchemy.orm

Base = sqlalchemy.orm.declarative_base()


class Ingredient(Base):
    __tablename__ = "ingredients"
    kind = sqla.Column(sqla.Text(), primary_key=True)
    loop_id = sqla.Column(sqla.Text(), primary_key=True)
    content = sqla.Column(sqla.JSON())

    @classmethod
    def from_dataclass(cls, ingredient: ocean.Ingredient):
        return cls(
            kind=ingredient.__class__.__name__.lower(),
            loop_id=str(ingredient.loop_id),
            content=ingredient.to_json(),
        )

    def to_ingredient(self):
        dataclass = {
            ingredient.__name__.lower(): ingredient
            for ingredient in [
                ocean.Event,
                ocean.Features,
                ocean.Prediction,
                ocean.Label,
            ]
        }[self.kind]
        return dataclass.from_json(self.content)


class SQLDataStore(DataStore):
    def __init__(self, url):
        self.engine = sqla.create_engine(url)

    def prepare(self):
        Base.metadata.create_all(self.engine)

    @contextlib.contextmanager
    def session(self):
        session_maker = sqlalchemy.orm.sessionmaker(self.engine)
        try:
            with session_maker.begin() as session:
                yield session
        finally:
            pass

    def store(self, kind, ingredient):
        row = Ingredient.from_dataclass(ingredient)
        with self.session() as session:
            session.add(row)

    def get(self, kind, loop_id):
        with self.session() as session:
            return (
                session.query(Ingredient)
                .filter_by(loop_id=str(loop_id))
                .first()
                .to_ingredient()
            )
