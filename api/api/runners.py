import fastapi

from api import db
import sqlmodel as sqlm

router = fastapi.APIRouter()


class Runner(sqlm.SQLModel, table=True):
    id: int | None = sqlm.Field(default=None, primary_key=True)
    name: str
    protocol: str
    url: str


@router.post("/")
def create_runner(runner: Runner):
    with db.session() as session:
        session.add(runner)
        session.commit()
        session.refresh(runner)
        return runner


@router.get("/", response_model=list[Runner])
def read_runners(offset: int = 0, limit: int = fastapi.Query(default=100, lte=100)):
    with db.session() as session:
        runners = session.exec(sqlm.select(Runner).offset(offset).limit(limit)).all()
        return runners


@router.get("/{runner_id}")
def read_runner(runner_id: int):
    with db.session() as session:
        runner = session.get(Runner, runner_id)
        if not runner:
            raise fastapi.HTTPException(status_code=404, detail="Runner not found")
        return runner
