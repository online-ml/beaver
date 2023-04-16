import contextlib
import os
import sqlmodel as sqlm


DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite://")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = sqlm.create_engine(DATABASE_URL, connect_args=connect_args)


def create_db_and_tables():
    sqlm.SQLModel.metadata.create_all(engine)


def get_session():
    with sqlm.Session(engine) as session:
        yield session


@contextlib.contextmanager
def session():
    # HACK
    from beaver.main import app

    try:
        session = next(app.dependency_overrides[get_session]())
        yield session
    except KeyError:
        session = next(db.get_session())
        yield session
    finally:
        session.close()
