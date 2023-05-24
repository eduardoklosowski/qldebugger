import logging
from typing import TYPE_CHECKING

from qldebugger.aws import get_client

if TYPE_CHECKING:
    from mypy_boto3_sqs.type_defs import ReceiveMessageResultTypeDef


logger = logging.getLogger(__name__)


def send_message(*, queue_name: str, message: str) -> None:
    logger.info('Sending message to %r queue...', queue_name)
    sqs = get_client('sqs')
    queue_url = sqs.get_queue_url(QueueName=queue_name)['QueueUrl']
    sqs.send_message(QueueUrl=queue_url, MessageBody=message)


def receive_message(
    *,
    queue_name: str,
    batch_size: int,
    maximum_batching_window: int,
) -> 'ReceiveMessageResultTypeDef':
    logger.debug('Receiving messages from %r queue...', queue_name)
    sqs = get_client('sqs')
    queue_url = sqs.get_queue_url(QueueName=queue_name)['QueueUrl']
    messages = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=batch_size,
        WaitTimeSeconds=maximum_batching_window,
    )
    if 'Messages' not in messages:
        logger.warning('No messages received from %r queue', queue_name)
        raise RuntimeWarning('No messages received')
    logger.info('Receved %d messages from %r queue', len(messages['Messages']), queue_name)
    return messages


def delete_messages(*, queue_name: str, messages: 'ReceiveMessageResultTypeDef') -> None:
    logger.debug('Deleting messages of %r queue...', queue_name)
    sqs = get_client('sqs')
    queue_url = sqs.get_queue_url(QueueName=queue_name)['QueueUrl']
    sqs.delete_message_batch(
        QueueUrl=queue_url,
        Entries=[
            {
                'Id': message['MessageId'],
                'ReceiptHandle': message['ReceiptHandle'],
            } for message in messages['Messages']
        ],
    )
    logger.info('Deleted %d messages from %r queue', len(messages['Messages']), queue_name)
