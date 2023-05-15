from __future__ import annotations

import fastapi
import sqlmodel as sqlm

from beaver import db, models

router = fastapi.APIRouter()


@router.post("/", status_code=201)
def create_job_runner(
    job_runner: models.JobRunner,
    session: sqlm.Session = fastapi.Depends(db.get_session),
):
    job_runner.save(session)
    return job_runner


@router.get("/", response_model=list[models.JobRunner])
def read_job_runners(
    offset: int = 0,
    limit: int = fastapi.Query(default=100, lte=100),
    session: sqlm.Session = fastapi.Depends(db.get_session),
):
    return session.exec(sqlm.select(models.JobRunner).offset(offset).limit(limit)).all()


@router.get("/{name}")
def read_job_runner(name: str, session: sqlm.Session = fastapi.Depends(db.get_session)):
    job_runner = session.get(models.JobRunner, name)
    if not job_runner:
        raise fastapi.HTTPException(status_code=404, detail="Job runner not found")
    return job_runner


@router.delete("/{name}", status_code=204)
def delete_job_runner(name: str, session: sqlm.Session = fastapi.Depends(db.get_session)):
    job_runner = session.get(models.JobRunner, name)
    if not job_runner:
        raise fastapi.HTTPException(status_code=404, detail="Job runner not found")
    job_runner.delete(session)
