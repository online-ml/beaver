import contextlib
import os

import sqlmodel as sqlm


DATABASE_URL = os.environ.get("DATABASE_URL")

engine = sqlm.create_engine(DATABASE_URL, echo=True)


def init_db():
    sqlm.SQLModel.metadata.drop_all(engine)
    sqlm.SQLModel.metadata.create_all(engine)


@contextlib.contextmanager
def session():
    session = sqlm.Session(engine)
    try:
        yield session
    finally:
        session.close()
