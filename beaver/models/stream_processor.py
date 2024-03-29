import sqlmodel

from beaver import infra as _infra, enums

from .base import Base


class StreamProcessor(Base, table=True):  # type: ignore[call-arg]
    __tablename__ = "stream_processor"

    # Attributes
    name: str = sqlmodel.Field(primary_key=True)
    protocol: enums.StreamProcessor
    url: str

    # Relationships
    projects: list["Project"] = sqlmodel.Relationship(  # noqa: F821
        back_populates="stream_processor"
    )

    @property
    def infra(self):
        if self.protocol == enums.StreamProcessor.sqlite:
            return _infra.SQLiteStreamProcessor(url=self.url)
        if self.protocol == enums.StreamProcessor.materialize:
            return _infra.MaterializeStreamProcessor(url=self.url)
        raise NotImplementedError
