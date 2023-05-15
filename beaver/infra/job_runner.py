from __future__ import annotations

import typing

import redis
import rq


class JobRunner(typing.Protocol):
    def start(self, task: typing.Callable) -> str:
        ...

    def stop(self, task_id: str) -> None:
        ...


class SynchronousJobRunner:
    def start(self, task):
        task()

    def stop(self, task_id):
        pass


class RQJobRunner:
    def __init__(self, redis_url):
        self.redis_url = redis_url

    def start(self, task):
        with rq.Connection(redis.Redis.from_url(self.redis_url)):
            return rq.Queue().enqueue(task).id

    def stop(self, task_id):
        with rq.Connection(rq.Redis.from_url(self.redis_url)):
            rq.Queue().fetch_job(task_id).cancel()
