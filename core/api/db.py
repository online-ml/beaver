import os
import sqlmodel as sqlm


DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite://")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = sqlm.create_engine(DATABASE_URL, echo=True, connect_args=connect_args)


def create_db_and_tables():
    sqlm.SQLModel.metadata.create_all(engine)


def get_session():
    with sqlm.Session(engine) as session:
        yield session
