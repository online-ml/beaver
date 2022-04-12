import beaver
import pytest


@pytest.fixture
def sqlite_data_store():
    data_store = beaver.data_store.SQLDataStore(url="sqlite://")
    data_store.build()
    return data_store


def test_store_event(sqlite_data_store):
    event = beaver.Event(content={"foo": "bar", "x": 1})
    sqlite_data_store.store_event(event)
    e = sqlite_data_store.get_event(event.loop_id)
    assert event.content == e.content


def test_store_label(sqlite_data_store):
    label = beaver.Label(content=True, loop_id=42)
    sqlite_data_store.store_label(label)
    e = sqlite_data_store.get_label(label.loop_id)
    assert label.content == e.content
