import logging
from typing import TYPE_CHECKING, Mapping

from qldebugger.aws import get_account_id, get_client

if TYPE_CHECKING:
    from mypy_boto3_sns.type_defs import MessageAttributeValueTypeDef
    from mypy_boto3_sqs.type_defs import ReceiveMessageResultTypeDef


logger = logging.getLogger(__name__)


def publish_message(
    *,
    topic_name: str,
    message: str,
    attributes: Mapping[str, 'MessageAttributeValueTypeDef'] = {},
) -> None:
    sns = get_client('sns')
    arn = f'arn:aws:sns:{sns.meta.region_name}:{get_account_id()}:{topic_name}'
    logger.info('Sending message to %r topic...', topic_name)
    sns.publish(
        TopicArn=arn,
        Message=message,
        MessageAttributes=attributes,
    )


def send_message(*, queue_name: str, message: str) -> None:
    sqs = get_client('sqs')
    queue_url = sqs.get_queue_url(QueueName=queue_name)['QueueUrl']
    logger.info('Sending message to %r queue...', queue_name)
    sqs.send_message(QueueUrl=queue_url, MessageBody=message)


def receive_message(
    *,
    queue_name: str,
    batch_size: int,
    maximum_batching_window: int,
) -> 'ReceiveMessageResultTypeDef':
    sqs = get_client('sqs')
    queue_url = sqs.get_queue_url(QueueName=queue_name)['QueueUrl']
    logger.debug('Receiving messages from %r queue...', queue_name)
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
    sqs = get_client('sqs')
    queue_url = sqs.get_queue_url(QueueName=queue_name)['QueueUrl']
    logger.debug('Deleting messages of %r queue...', queue_name)
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
