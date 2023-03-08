import fastapi
import psycopg
import sqlmodel as sqlm

from api import db

router = fastapi.APIRouter()


class Processor(sqlm.SQLModel, table=True):  # type: ignore[call-arg]
    id: int | None = sqlm.Field(default=None, primary_key=True)
    name: str
    protocol: str
    url: str

    feature_sets: list["FeatureSet"] = sqlm.Relationship(back_populates="processor")  # type: ignore[name-defined] # noqa
    targets: list["Target"] = sqlm.Relationship(back_populates="processor")  # type: ignore[name-defined] # noqa

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


@router.post("/")
def create_processor(processor: Processor):
    with db.session() as session:
        session.add(processor)
        session.commit()
        session.refresh(processor)
        return processor


@router.get("/", response_model=list[Processor])
def read_processors(offset: int = 0, limit: int = fastapi.Query(default=100, lte=100)):
    with db.session() as session:
        return session.exec(sqlm.select(Processor).offset(offset).limit(limit)).all()


@router.get("/{processor_id}")
def read_processor(processor_id: int):
    with db.session() as session:
        processor = session.get(Processor, processor_id)
        if not processor:
            raise fastapi.HTTPException(status_code=404, detail="Processor not found")
        return processor
