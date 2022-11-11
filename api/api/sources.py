from typing import Any, List

import fastapi
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from api import db
import sqlmodel as sqlm

router = fastapi.APIRouter()


class Source(sqlm.SQLModel, table=True):
    id: int | None = sqlm.Field(default=None, primary_key=True)
    name: str
    protocol: str
    host: str
    port: int


@router.post("/")
def create_source(source: Source):
    with db.session() as session:
        session.add(source)
        session.commit()
        session.refresh(session)
        return session


@router.get("/", response_model=list[Source])
def read_sources(
    offset: int = 0, limit: int = fastapi.Query(default=100, lte=100)
) -> Any:
    with db.session() as session:
        sources = session.exec(sqlm.select(Source).offset(offset).limit(limit)).all()
        return sources
