import fastapi
import sqlmodel as sqlm

from core import infra, enums


class MessageBus(sqlm.SQLModel, table=True):  # type: ignore[call-arg]
    id: int | None = sqlm.Field(default=None, primary_key=True)
    name: str
    protocol: enums.MessageBus
    url: str | None = None

    @property
    def message_bus(self):
        if self.protocol == enums.MessageBus.kafka:
            return infra.KafkaMessageBus(url=self.url)
        if self.protocol == enums.MessageBus.dummy:
            return infra.DummyMessageBus()
        raise NotImplementedError
