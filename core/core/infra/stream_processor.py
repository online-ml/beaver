import contextlib
import datetime as dt
import sqlite3
import typing


class StreamProcessor(typing.Protocol):
    def create_view(self, name: str, query: str):
        ...

    def stream_view(self, name: str, query: str) -> typing.Generator[dict, None, None]:
        ...


class SQLiteStreamProcessor:
    def __init__(self, url: str):
        self.url = url

    def create_view(self, name, query):
        with sqlite3.connect(self.url) as con:
            con.execute(f"CREATE VIEW {name} AS {query}")

    def create_performance_view(self, project_name):
        self.create_view(
            name=f"performance_{project_name}",
            query=f"""
            SELECT
                experiment_name,
                COUNT(*) AS n_predictions
            FROM predictions
            WHERE project = '{project_name}'
            GROUP BY 1
            """,
        )

    def get_performance_view(self, project_name):
        with sqlite3.connect(self.url) as con:
            con.row_factory = sqlite3.Row
            rows = list(
                map(dict, con.execute(f"SELECT * FROM performance_{project_name}"))
            )
        return rows

    def stream_view(self, name, since):
        with sqlite3.connect(self.url) as con:
            con.row_factory = sqlite3.Row
            rows = list(map(dict, con.execute(f"SELECT * FROM {name}")))
        yield from rows


class MaterializeStreamProcessor:
    def __init__(self, url: str):
        self.url = url

    def execute(self, sql):
        conn = psycopg.connect(self.url)
        conn.autocommit = True
        with conn.cursor() as cur:
            for q in sql.split(";"):
                cur.execute(q)

    def get_first_row(self, sql):
        conn = psycopg.connect(self.url)
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute(sql)
            return dict(zip((desc[0] for desc in cur.description), cur.fetchone()))

    def stream(self, view_name):

        # Let's query the view to see what it contains. That way we can associate each feature with
        # a name.
        conn = psycopg.connect(self.url)
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute(f"SHOW COLUMNS FROM {view_name}")
            schema = cur.fetchall()
            columns = ["mz_timestamp", "mz_diff"] + [c[0] for c in schema]

        conn = psycopg.connect(self.url)
        with conn.cursor() as cur:
            for row in cur.stream(f"TAIL {view_name}"):
                named_row = dict(zip(columns, row))
                del named_row["mz_timestamp"]
                del named_row["mz_diff"]
                yield named_row
