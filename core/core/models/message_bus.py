import fastapi
import sqlmodel as sqlm

from core import infra, enums


class MessageBus(sqlm.SQLModel, table=True):  # type: ignore[call-arg]
    name: str = sqlm.Field(primary_key=True)
    protocol: enums.MessageBus
    url: str

    @property
    def message_bus(self):
        if self.protocol == enums.MessageBus.sqlite:
            return infra.SQLiteMessageBus(url=self.url)
        if self.protocol == enums.MessageBus.kafka:
            return infra.KafkaMessageBus(url=self.url)
        if self.protocol == enums.MessageBus.redpanda:
            return infra.RedpandaMessageBus(url=self.url)
        raise NotImplementedError
