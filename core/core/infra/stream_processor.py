import typing


class StreamProcessor(typing.Protocol):
    @property
    def topics(self) -> typing.List[str]:
        ...

    def send(self, topic: str, key: str, value: str | dict) -> None:
        ...
