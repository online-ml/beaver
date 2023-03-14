import fastapi
import sqlmodel as sqlm

from core import infra, enums


class StreamProcessor(sqlm.SQLModel, table=True):  # type: ignore[call-arg]
    name: str = sqlm.Field(primary_key=True)
    protocol: enums.StreamProcessor
    url: str
