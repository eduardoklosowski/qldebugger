import logging

from ..aws import get_client

logger = logging.getLogger(__name__)


def send_message(*, queue_name: str, message: str) -> None:
    logger.info('Sending message to %r queue...', queue_name)
    client = get_client('sqs')
    queue_url = client.get_queue_url(QueueName=queue_name)['QueueUrl']
    client.send_message(QueueUrl=queue_url, MessageBody=message)
