from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import RedisScheduleSource

from {{cookiecutter.project_name}}.services.taskiq.broker import broker
from {{cookiecutter.project_name}}.settings import settings

redis_source = RedisScheduleSource(str(settings.redis.url))


scheduler = TaskiqScheduler(
    broker,
    [
        redis_source,
        LabelScheduleSource(broker),
    ],
)
