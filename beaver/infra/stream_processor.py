from __future__ import annotations

import datetime as dt
import sqlite3
import typing

import psycopg


class StreamProcessor(typing.Protocol):
    def execute(self, query: str):
        ...

    def query(self, query: str) -> typing.Generator[dict, None, None]:
        ...

    def create_view(self, name: str, query: str):
        ...

    def stream_view(
        self, name: str, since: dt.datetime | None = None
    ) -> typing.Generator[dict, None, None]:
        ...


class SQLiteStreamProcessor:
    def __init__(self, url: str):
        self.url = url

    def execute(self, query):
        with sqlite3.connect(self.url) as con:
            con.execute(query)

    def query(self, query):
        with sqlite3.connect(self.url) as con:
            con.row_factory = sqlite3.Row
            rows = list(map(dict, con.execute(query)))
        yield from rows

    def create_view(self, name, query):
        with sqlite3.connect(self.url) as con:
            con.execute(f"DROP VIEW IF EXISTS {name}")
            con.execute(f"CREATE VIEW {name} AS {query}")

    def stream_view(self, name, since=None):
        query = f"SELECT * FROM {name}"
        if since:
            query += f" WHERE ts > '{since}'"
        yield from self.query(query)


class MaterializeStreamProcessor:
    def __init__(self, url: str):
        self.url = url

    def execute(self, query):
        conn = psycopg.connect(self.url)
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(query)

    def query(self, query):
        conn = psycopg.connect(self.url)
        with conn.cursor() as cur:
            cur.execute(query)
            columns = [desc[0] for desc in cur.description]
            for row in cur:
                yield dict(zip(columns, row))

    def create_view(self, name, query):
        conn = psycopg.connect(self.url)
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(f"DROP VIEW IF EXISTS {name}")
            cur.execute(f"CREATE VIEW {name} AS ({query})")

    def stream_view(self, name, since=None):
        # TODO: handle since

        # Let's query the view to see what it contains. That way we can associate each feature with
        # a name.
        conn = psycopg.connect(self.url)
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute(f"SHOW COLUMNS FROM {name}")
            schema = cur.fetchall()
            columns = ["mz_timestamp", "mz_diff"] + [c[0] for c in schema]

        conn = psycopg.connect(self.url)
        with conn.cursor() as cur:
            for row in cur.stream(f"TAIL {name}"):
                named_row = dict(zip(columns, row))
                del named_row["mz_timestamp"]
                del named_row["mz_diff"]
                yield named_row
