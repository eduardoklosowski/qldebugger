import logging

from ..aws import get_client
from ..config import get_config

logger = logging.getLogger(__name__)


def create_queues() -> None:
    client = get_client('sqs')
    queues = get_config().queues

    for queue_name in queues.keys():
        logger.info('Creating %r queue...', queue_name)
        client.create_queue(QueueName=queue_name)
