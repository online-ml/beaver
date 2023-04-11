import pathlib
import pytest
import sqlmodel
from core import enums, models


@pytest.fixture(name="session")
def session_fixture():
    engine = sqlmodel.create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=sqlmodel.pool.StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with sqlmodel.Session(engine) as session:
        yield session


@pytest.fixture(name="sqlite_mb_path")
def sqlite_mb_path():
    here = pathlib.Path(__file__).parent
    yield here / "message_bus.db"
    (here / "message_bus.db").unlink(missing_ok=True)


@pytest.fixture(name="sqlite_message_bus")
def sqlite_message_bus(session_fixture, sqlite_mb_path: pathlib.Path):
    message_bus = models.MessageBus(
        name="sqlite_message_bus",
        protocol=enums.MessageBus.sqlite,
        url=str(sqlite_mb_path),
    )
    session.add(message_bus)
    session.commit()
    session.refresh(message_bus)
    return message_bus


@pytest.fixture(name="sqlite_stream_processor")
def sqlite_stream_processor(session_fixture, sqlite_mb_path: pathlib.Path):
    message_bus = models.MessageBus(
        name="sqlite_stream_processor",
        protocol=enums.MessageBus.sqlite,
        url=str(sqlite_mb_path),
    )
    session.add(message_bus)
    session.commit()
    session.refresh(message_bus)
    return message_bus


@pytest.mark.parametrize(
    "message_bus, stream_processor",
    [
        pytest.param(mb, sp, id=f"mb={mb.__name__}:sp={sp.__name__}")
        for mb, sp in [(sqlite_message_bus, sqlite_stream_processor)]
    ],
)
def test_iter_dataset(message_bus, stream_processor):
    """Test the iter_dataset function using different message buses and stream processors."""
