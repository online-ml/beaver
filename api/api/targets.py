import fastapi
import sqlmodel as sqlm

from api import db, processors, tasks

router = fastapi.APIRouter()


class Target(sqlm.SQLModel, table=True):  # type: ignore[call-arg]
    id: int | None = sqlm.Field(default=None, primary_key=True)
    name: str
    query: str
    key_field: str
    target_field: str
    task: tasks.TaskEnum

    processor_id: int = sqlm.Field(foreign_key="processor.id")
    processor: processors.Processor = sqlm.Relationship(back_populates="targets")
    experiments: list["Experiment"] = sqlm.Relationship(back_populates="target")  # type: ignore[name-defined] # noqa

    def create(self, session):
        processor = session.get(processors.Processor, self.processor_id)
        if not processor:
            raise fastapi.HTTPException(status_code=404, detail="Processor not found")
        processor.execute(self.query)

        session.add(self)
        session.commit()
        session.refresh(self)

        return self


@router.post("/")
def create_target(target: Target):
    with db.session() as session:
        return target.create(session)


@router.get("/")
def read_targets(offset: int = 0, limit: int = fastapi.Query(default=100, lte=100)):
    with db.session() as session:
        return session.exec(
            sqlm.select(Target.id, Target.name, Target.key_field, Target.target_field)
            .offset(offset)
            .limit(limit)
        ).all()


@router.get("/{target_id}")
def read_target(target_id: int):
    with db.session() as session:
        target = session.get(Target, target_id)
        if not target:
            raise fastapi.HTTPException(status_code=404, detail="Target not found")
        return target
