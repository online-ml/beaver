import contextlib
import os

import sqlmodel as sqlm

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/postgres"
)

engine = sqlm.create_engine(DATABASE_URL, echo=True)


@contextlib.contextmanager
def session():
    session = sqlm.Session(engine)
    try:
        yield session
    finally:
        session.close()
