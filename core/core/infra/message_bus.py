import collections
import contextlib
import datetime as dt
import json
import typing
import kafka
import sqlite3
import pydantic


class Message(pydantic.BaseModel):
    topic: str
    key: str
    value: str
    created_at: dt.datetime = pydantic.Field(default_factory=dt.datetime.utcnow)


class MessageBus(typing.Protocol):
    @property
    def topic_names(self) -> typing.List[str]:
        ...

    def send(self, message: Message) -> None:
        ...


class SQLiteMessageBus:
    def __init__(self, url: str):
        self.url = url
        with self.connection() as con:
            cur = con.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS messages(topic, key, value, created_at)"
            )

    @contextlib.contextmanager
    def connection(self):
        con = sqlite3.connect(self.url)
        try:
            yield con
        finally:
            con.close()

    @property
    def topic_names(self) -> typing.List[str]:
        with self.connection() as con:
            cur = con.cursor()
            return cur.execute("SELECT DISTINCT topic FROM messages").fetchall()

    def send(self, message: Message) -> None:
        with self.connection() as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO messages (topic, key, value, created_at) VALUES (?, ?, ?, ?)",
                (
                    message.topic,
                    message.key,
                    message.value,
                    message.created_at,
                ),
            )


class KafkaMessageBus(kafka.KafkaProducer):
    def __init__(self, url: str):
        super().__init__(
            bootstrap_servers=[url],
            key_serializer=str.encode,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    @property
    def topic_names(self) -> typing.List[str]:
        return list(self.list_topics().keys())


class RedpandaMessageBus(kafka.KafkaProducer):
    def __init__(self, url: str):
        super().__init__(
            bootstrap_servers=[url],
            key_serializer=str.encode,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    @property
    def topic_names(self) -> typing.List[str]:
        return list(self.list_topics().keys())
