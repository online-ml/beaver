from __future__ import annotations

import datetime as dt

import sqlmodel


class Base(sqlmodel.SQLModel):
    created_at: dt.datetime = sqlmodel.Field(
        default=dt.datetime.utcnow(), nullable=False
    )

    def save(self, session: sqlmodel.Session):
        session.add(self)
        session.commit()
        session.refresh(self)
        return self

    def delete(self, session: sqlmodel.Session):
        session.delete(self)
        session.commit()
