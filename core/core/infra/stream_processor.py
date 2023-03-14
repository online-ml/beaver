import contextlib
import sqlite3
import typing


class StreamProcessor(typing.Protocol):
    def run_query(self, query: str):
        ...


class SQLiteStreamProcessor:
    def __init__(self, url: str):
        self.url = url

    @contextlib.contextmanager
    def connection(self):
        con = sqlite3.connect(self.url)
        try:
            yield con
        finally:
            con.close()

    def run_query(self, query: str):
        with self.connection() as con:
            cur = con.cursor()
            return cur.execute(query).fetchall()


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
