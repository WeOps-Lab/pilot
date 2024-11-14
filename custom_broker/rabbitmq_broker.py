from asyncio import AbstractEventLoop
from typing import Optional, Text, Union, Any, List, Tuple

from loguru import logger
from rasa.core.brokers.pika import PikaEventBroker, RABBITMQ_EXCHANGE

from core.server_settings import server_settings


class RabbitMQEventBroker(PikaEventBroker):
    def __init__(self,
                 host: Text,
                 username: Text,
                 password: Text,
                 port: Union[int, Text] = 5672,
                 queues: Union[List[Text], Tuple[Text, ...], Text, None] = None,
                 should_keep_unpublished_messages: bool = True,
                 raise_on_failure: bool = False,
                 event_loop: Optional[AbstractEventLoop] = None,
                 connection_attempts: int = 20,
                 retry_delay_in_seconds: float = 5,
                 exchange_name: Text = RABBITMQ_EXCHANGE,
                 **kwargs: Any, ):
        super().__init__(host, username, password, port, queues, should_keep_unpublished_messages, raise_on_failure,
                         event_loop, connection_attempts, retry_delay_in_seconds, exchange_name, **kwargs)

    def publish(self, event, headers=None):
        event["bot_id"] = server_settings.munchkin_bot_id
        super().publish(event, headers)
        logger.info(f"RabbitMQEventBroker publish event: {event}")
