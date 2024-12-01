from taskiq_aio_pika import AioPikaBroker

from core.constants import BrokerExchange, BrokerQueue
from settings import BROKER_SETTINGS


broker = AioPikaBroker(
    BROKER_SETTINGS.dsn,
    exchange_name=BrokerExchange.APP,
    queue_name=BrokerQueue.MESSAGES,
    declare_exchange=True,
    declare_queues=True,
)
