import collections
import typing
import kafka


class MessageBus(typing.Protocol):
    @property
    def topic_names(self) -> typing.List[str]:
        ...

    def send(self, topic: str, key: str, value: str | dict) -> None:
        ...


class DummyMessageBus:
    def __init__(self):
        self.topics = collections.defaultdict(list)

    @property
    def topic_names(self) -> typing.List[str]:
        return list(self.topics.keys())

    def send(self, topic: str, key: str, value: str | dict) -> None:
        self.topics[topic].append((key, value))


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
