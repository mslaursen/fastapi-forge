from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import RedisScheduleSource

from src.services.taskiq.broker import broker
from src.settings import settings

redis_source = RedisScheduleSource(str(settings.redis.url))


scheduler = TaskiqScheduler(
    broker,
    [
        redis_source,
        LabelScheduleSource(broker),
    ],
)
