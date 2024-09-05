import json
import logging
from typing import TYPE_CHECKING, Dict

from botocore.exceptions import ClientError
from graphlib import TopologicalSorter

from qldebugger.aws import get_account_id, get_client
from qldebugger.config import get_config
from qldebugger.config.file_parser import ConfigQueue, ConfigSecretString

if TYPE_CHECKING:
    from mypy_boto3_sqs.literals import QueueAttributeNameType

logger = logging.getLogger(__name__)


def create_secrets() -> None:
    secretsmanager = get_client('secretsmanager')
    secrets = get_config().secrets

    for name, value in secrets.items():
        try:
            secretsmanager.describe_secret(SecretId=name)
            if isinstance(value, ConfigSecretString):
                logger.info('Updating %r string secret...', name)
                secretsmanager.put_secret_value(SecretId=name, SecretString=value.get_value())
            else:
                logger.info('Updating %r binary secret...', name)
                secretsmanager.put_secret_value(SecretId=name, SecretBinary=value.get_value())
        except ClientError:
            if isinstance(value, ConfigSecretString):
                logger.info('Creating %r string secret...', name)
                secretsmanager.create_secret(Name=name, SecretString=value.get_value())
            else:
                logger.info('Creating %r binary secret...', name)
                secretsmanager.create_secret(Name=name, SecretBinary=value.get_value())


def create_topics() -> None:
    sns = get_client('sns')
    topics = get_config().topics

    for topic_name in topics:
        logger.info('Creating %r topic...', topic_name)
        sns.create_topic(Name=topic_name)


def create_queues() -> None:
    sqs = get_client('sqs')
    queues = get_config().queues
    order = TopologicalSorter(
        {
            name: {queue.redrive_policy.dead_letter_queue} if queue.redrive_policy else set()
            for name, queue in queues.items()
        }
    ).static_order()

    for queue_name in order:
        attributes: Dict['QueueAttributeNameType', str] = {}
        if redrive_policy := queues.get(queue_name, ConfigQueue()).redrive_policy:
            logger.debug('Checking dead letter queue (%r) for %r...', redrive_policy.dead_letter_queue, queue_name)
            dead_letter_queue_attributes = sqs.get_queue_attributes(
                QueueUrl=redrive_policy.dead_letter_queue, AttributeNames=['QueueArn']
            )
            attributes['RedrivePolicy'] = json.dumps(
                {
                    'deadLetterTargetArn': dead_letter_queue_attributes['Attributes']['QueueArn'],
                    'maxReceiveCount': redrive_policy.max_receive_count,
                }
            )
        try:
            queue_url = sqs.get_queue_url(QueueName=queue_name)
            logger.info('Updating %r queue...', queue_name)
            sqs.set_queue_attributes(QueueUrl=queue_url['QueueUrl'], Attributes=attributes)
        except ClientError:
            logger.info('Creating %r queue...', queue_name)
            sqs.create_queue(QueueName=queue_name, Attributes=attributes)


def subscribe_topics() -> None:
    sns = get_client('sns')
    topics = get_config().topics
    account_id = get_account_id()
    region = sns.meta.region_name

    subscriptions = sns.list_subscriptions()['Subscriptions']
    for subscription in subscriptions:
        logger.info('Unsubscribing %r queue (%r)...', subscription['Endpoint'], subscription['SubscriptionArn'])
        sns.unsubscribe(SubscriptionArn=subscription['SubscriptionArn'])

    for topic_name, config_topic in topics.items():
        for subscriber in config_topic.subscribers:
            logger.info('Subscribing %r topic to %r queue...', topic_name, subscriber.queue)
            attributes = {
                'RawMessageDelivery': 'true' if subscriber.raw_message_delivery else 'false',
            }
            if subscriber.filter_policy is not None:
                attributes['FilterPolicy'] = subscriber.filter_policy
            sns.subscribe(
                TopicArn=f'arn:aws:sns:{region}:{account_id}:{topic_name}',
                Protocol='sqs',
                Endpoint=f'arn:aws:sqs:{region}:{account_id}:{subscriber.queue}',
                Attributes=attributes,
            )
