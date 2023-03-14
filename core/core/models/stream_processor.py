import fastapi
import sqlmodel as sqlm

from core import infra, enums


class StreamProcessor(sqlm.SQLModel, table=True):  # type: ignore[call-arg]
    __tablename__ = "stream_processor"

    name: str = sqlm.Field(primary_key=True)
    protocol: enums.StreamProcessor
    url: str

    projects: list["Project"] = sqlm.Relationship(back_populates="stream_processor")

    @property
    def infra(self):
        if self.protocol == enums.StreamProcessor.sqlite:
            return infra.SQLiteStreamProcessor(url=self.url)
        raise NotImplementedError
