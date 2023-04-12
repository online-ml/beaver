import fastapi
import sqlmodel

from core import infra as _infra, enums

from .base import Base


class MessageBus(Base, table=True):  # type: ignore[call-arg]
    __tablename__ = "message_bus"

    # Attributes
    name: str = sqlmodel.Field(primary_key=True)
    protocol: enums.MessageBus
    url: str

    # Relationships
    projects: list["Project"] = sqlmodel.Relationship(back_populates="message_bus")  # type: ignore[name-defined]

    @property
    def infra(self):
        if self.protocol == enums.MessageBus.sqlite:
            return _infra.SQLiteMessageBus(url=self.url)
        if self.protocol == enums.MessageBus.kafka:
            return _infra.KafkaMessageBus(url=self.url)
        if self.protocol == enums.MessageBus.redpanda:
            return _infra.RedpandaMessageBus(url=self.url)
        raise NotImplementedError
