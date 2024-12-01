import logging

from taskiq import TaskiqEvents
from taskiq_aio_pika import AioPikaBroker

from core.constants import BrokerExchange, BrokerQueue
from infrastructure.databases import database
from settings import BROKER_SETTINGS


logger = logging.getLogger("uvicorn")


broker = AioPikaBroker(
    BROKER_SETTINGS.dsn,
    exchange_name=BrokerExchange.APP,
    queue_name=BrokerQueue.MESSAGES,
    declare_exchange=True,
    declare_queues=True,
)


@broker.on_event(TaskiqEvents.WORKER_STARTUP, TaskiqEvents.CLIENT_STARTUP)
async def start_up(*args, **kwargs) -> None:
    if not database.is_init():
        await database.init()

    logger.info("Broker started")


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN, TaskiqEvents.CLIENT_SHUTDOWN)
async def shutdown(*args, **kwargs) -> None:
    if database.is_init():
        await database.close_connection()

    logger.info("Broker stopped")
