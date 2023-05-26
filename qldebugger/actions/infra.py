import logging

from botocore.exceptions import ClientError

from qldebugger.aws import get_account_id, get_client
from qldebugger.config import get_config
from qldebugger.config.file_parser import ConfigSecretString

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

    for queue_name in queues:
        logger.info('Creating %r queue...', queue_name)
        sqs.create_queue(QueueName=queue_name)


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
