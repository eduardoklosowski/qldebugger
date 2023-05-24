import logging

from qldebugger.aws import get_client
from qldebugger.config import get_config

logger = logging.getLogger(__name__)


def create_topics() -> None:
    sns = get_client('sns')
    topics = get_config().topics

    for topic_name in topics:
        logger.info('Creating %r topic...', topic_name)
        sns.create_topic(Name=topic_name)


def create_queues() -> None:
    sqs = get_client('sqs')
    queues = get_config().queues

    for queue_name in queues:
        logger.info('Creating %r queue...', queue_name)
        sqs.create_queue(QueueName=queue_name)
