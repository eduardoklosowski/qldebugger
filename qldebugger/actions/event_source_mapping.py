import logging
from typing import TYPE_CHECKING

from qldebugger.aws import get_account_id, get_client
from qldebugger.config import get_config

from .lambda_ import run_lambda
from .message import delete_messages, receive_message

if TYPE_CHECKING:
    from aws_lambda_typing.events import SQSEvent
    from mypy_boto3_sqs.type_defs import ReceiveMessageResultTypeDef

logger = logging.getLogger(__name__)


def receive_messages_and_run_lambda(*, event_source_mapping_name: str) -> None:
    sqs = get_client('sqs')
    event_source_mapping = get_config().event_source_mapping[event_source_mapping_name]

    queue_arn = f'arn:{sqs.meta.partition}:sqs:{sqs.meta.region_name}:{get_account_id()}:{event_source_mapping.queue}'

    logger.debug('Execute %r event source mapping...', event_source_mapping_name)
    messages = receive_message(
        queue_name=event_source_mapping.queue,
        batch_size=event_source_mapping.batch_size,
        maximum_batching_window=event_source_mapping.maximum_batching_window,
    )
    event = convert_sqs_messages_to_event(
        aws_region=sqs.meta.region_name,
        event_source=f'{sqs.meta.partition}:sqs',
        event_source_arn=queue_arn,
        messages=messages,
    )
    run_lambda(lambda_name=event_source_mapping.function_name, event=event)
    delete_messages(queue_name=event_source_mapping.queue, messages=messages)


def convert_sqs_messages_to_event(
    *,
    aws_region: str,
    event_source: str,
    event_source_arn: str,
    messages: 'ReceiveMessageResultTypeDef',
) -> 'SQSEvent':
    return {
        'Records': [
            {
                'messageId': message['MessageId'],
                'receiptHandle': message['ReceiptHandle'],
                'body': message['Body'],
                'attributes': {},
                'messageAttributes': {},
                'md5OfBody': message['MD5OfBody'],
                'eventSource': event_source,
                'eventSourceARN': event_source_arn,
                'awsRegion': aws_region,
            }
            for message in messages['Messages']
        ],
    }
