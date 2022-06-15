from __future__ import annotations
import abc
import contextlib
import dataclasses
import datetime as dt
import graphlib
import uuid
import pathlib
import re

import beaver
import sqlalchemy as sqla
import sqlalchemy.orm


class DataStore(abc.ABC):
    def build(self):
        ...

    @abc.abstractmethod
    def store(self, kind: str, loop_part: beaver.LoopPart):
        ...

    def store_event(self, event: beaver.Event):
        return self.store("event", event)

    def store_features(self, features: beaver.Features):
        return self.store("features", features)

    def store_prediction(self, prediction: beaver.Prediction):
        return self.store("prediction", prediction)

    def store_label(self, label: beaver.Label):
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


Base = sqlalchemy.orm.declarative_base()


class LoopPart(Base):
    __abstract__ = True
    loop_id = sqla.Column(sqla.Text(), primary_key=True)
    created_at = sqla.Column(sqla.DateTime(), default=dt.datetime.now)


class Event(LoopPart):
    __tablename__ = "events"
    content = sqla.Column(sqla.JSON())

    @classmethod
    def from_dataclass(cls, event: beaver.Event):
        return cls(loop_id=str(event.loop_id), content=event.content)

    def to_dataclass(self):
        return beaver.Event(loop_id=self.loop_id, content=self.content)


class Features(LoopPart):
    __tablename__ = "features"
    content = sqla.Column(sqla.JSON())
    model_name = sqla.Column(sqla.Text(), primary_key=True)

    @classmethod
    def from_dataclass(cls, features: beaver.Features):
        return cls(
            loop_id=str(features.loop_id),
            content=features.content,
            model_name=features.model_name,
        )

    def to_dataclass(self):
        return beaver.Features(
            loop_id=self.loop_id, content=self.content, model_name=self.model_name
        )


class Prediction(LoopPart):
    __tablename__ = "predictions"
    content = sqla.Column(sqla.JSON())
    model_name = sqla.Column(sqla.Text(), primary_key=True)

    @classmethod
    def from_dataclass(cls, prediction: beaver.Prediction):
        return cls(
            loop_id=str(prediction.loop_id),
            content=prediction.content,
            model_name=prediction.model_name,
        )

    def to_dataclass(self):
        return beaver.Prediction(
            loop_id=self.loop_id, content=self.content, model_name=self.model_name
        )


class Label(LoopPart):
    __tablename__ = "labels"
    content = sqla.Column(sqla.JSON())

    @classmethod
    def from_dataclass(cls, label: beaver.Label):
        return cls(loop_id=str(label.loop_id), content=label.content)

    def to_dataclass(self):
        return beaver.Label(loop_id=self.loop_id, content=self.content)


@dataclasses.dataclass
class View:
    path: pathlib.Path

    def __hash__(self):
        return hash(self.name)

    @property
    def name(self):
        return self.path.stem

    @property
    def query(self):
        return self.path.read_text().rstrip().rstrip(";")

    @property
    def cte_names(self):
        pattern = r'"?(?P<table>\w+)"? AS \('
        return {match.group("table") for match in re.finditer(pattern, self.query)}

    @property
    def dependencies(self):
        pattern = r'(FROM|(LEFT|RIGHT|INNER|OUTER)? JOIN) "?(?P<table>\w+)"?'
        tables = {match.group("table") for match in re.finditer(pattern, self.query)}
        return tables - self.cte_names


class SQLDataStore(DataStore):
    def __init__(self, url):
        self.engine = sqla.create_engine(url)

    def build(self):
        Base.metadata.create_all(self.engine)

        here = pathlib.Path(__file__)
        views = [View(path) for path in here.parent.glob("views/*.sql")]
        views = {view.name: view for view in views}

        dependencies = {view: set() for view in views.values()}
        for view in views.values():
            for dep in view.dependencies & views.keys():
                dependencies[view].add(views[dep])

        for view in graphlib.TopologicalSorter(dependencies).static_order():
            self.engine.execute(sqla.text(f"DROP VIEW IF EXISTS {view.name}"))
            self.engine.execute(sqla.text(f"CREATE VIEW {view.name} AS {view.query}"))

    def clear(self):
        with contextlib.closing(self.engine.connect()) as con:
            trans = con.begin()
            for table in reversed(Base.metadata.sorted_tables):
                con.execute(table.delete())
            trans.commit()

    @contextlib.contextmanager
    def session(self):
        session_maker = sqlalchemy.orm.sessionmaker(self.engine)
        try:
            with session_maker.begin() as session:
                yield session
        finally:
            pass

    def store(self, kind, loop_part):
        row = {
            "event": Event,
            "features": Features,
            "prediction": Prediction,
            "label": Label,
        }[kind].from_dataclass(loop_part)
        with self.session() as session:
            session.add(row)

    def get(self, kind, loop_id):
        klass = {
            "event": Event,
            "features": Features,
            "prediction": Prediction,
            "label": Label,
        }[kind]
        with self.session() as session:
            return (
                session.query(klass)
                .filter_by(loop_id=str(loop_id))
                .first()
                .to_dataclass()
            )
