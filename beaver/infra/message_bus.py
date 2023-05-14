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
        with sqlite3.connect(self.url) as con:
            con.execute(
                "CREATE TABLE IF NOT EXISTS messages(topic, key, value, created_at)"
            )

    @property
    def topic_names(self) -> typing.List[str]:
        with sqlite3.connect(self.url) as con:
            rows = con.execute("SELECT DISTINCT topic FROM messages").fetchall()
        return rows

    def send(self, message: Message) -> None:
        with sqlite3.connect(self.url) as con:
            con.execute(
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
            value_serializer=lambda v: v.encode("utf-8"),
        )

    @property
    def topic_names(self) -> typing.List[str]:
        return list(self.list_topics().keys())

    def send(self, message: Message) -> None:
        super().send(
            topic=message.topic, value=message.value, key=message.key
        )


class RedpandaMessageBus(KafkaMessageBus):
    ...
