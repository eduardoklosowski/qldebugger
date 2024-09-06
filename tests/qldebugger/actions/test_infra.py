import json
from collections import OrderedDict
from random import randint
from typing import Dict
from unittest.mock import Mock, call, patch

from botocore.exceptions import ClientError

from qldebugger.actions.infra import create_queues, create_secrets, create_topics, subscribe_topics
from qldebugger.config.file_parser import (
    ConfigQueue,
    ConfigQueueRedrivePolicy,
    ConfigSecretBinary,
    ConfigSecretString,
    ConfigTopic,
    ConfigTopicSubscriber,
)
from tests.utils import randstr


class TestCreateSecrets:
    @patch('qldebugger.actions.infra.get_client')
    @patch('qldebugger.actions.infra.get_config')
    def test_create_string_secrets(self, mock_get_config: Mock, mock_get_client: Mock) -> None:
        secrets = {randstr(): randstr() for _ in range(randint(2, 5))}

        mock_get_config.return_value.secrets = {
            name: ConfigSecretString(string=value) for name, value in secrets.items()
        }
        mock_get_client.return_value.describe_secret.side_effect = ClientError({}, '')

        create_secrets()

        mock_get_client.assert_called_once_with('secretsmanager')
        assert mock_get_client.return_value.create_secret.call_count == len(secrets)
        for name, value in secrets.items():
            mock_get_client.return_value.create_secret.assert_any_call(Name=name, SecretString=value)
        mock_get_client.return_value.put_secret_value.assert_not_called()

    @patch('qldebugger.actions.infra.get_client')
    @patch('qldebugger.actions.infra.get_config')
    def test_create_binary_secrets(self, mock_get_config: Mock, mock_get_client: Mock) -> None:
        secrets = {randstr(): randstr().encode() for _ in range(randint(2, 5))}

        mock_get_config.return_value.secrets = {
            name: ConfigSecretBinary(binary=value) for name, value in secrets.items()
        }
        mock_get_client.return_value.describe_secret.side_effect = ClientError({}, '')

        create_secrets()

        mock_get_client.assert_called_once_with('secretsmanager')
        assert mock_get_client.return_value.create_secret.call_count == len(secrets)
        for name, value in secrets.items():
            mock_get_client.return_value.create_secret.assert_any_call(Name=name, SecretBinary=value)
        mock_get_client.return_value.put_secret_value.assert_not_called()

    @patch('qldebugger.actions.infra.get_client')
    @patch('qldebugger.actions.infra.get_config')
    def test_update_string_secrets(self, mock_get_config: Mock, mock_get_client: Mock) -> None:
        secrets = {randstr(): randstr() for _ in range(randint(2, 5))}

        mock_get_config.return_value.secrets = {
            name: ConfigSecretString(string=value) for name, value in secrets.items()
        }

        create_secrets()

        mock_get_client.assert_called_once_with('secretsmanager')
        assert mock_get_client.return_value.put_secret_value.call_count == len(secrets)
        for name, value in secrets.items():
            mock_get_client.return_value.put_secret_value.assert_any_call(SecretId=name, SecretString=value)
        mock_get_client.return_value.create_secret.assert_not_called()

    @patch('qldebugger.actions.infra.get_client')
    @patch('qldebugger.actions.infra.get_config')
    def test_update_binary_secrets(self, mock_get_config: Mock, mock_get_client: Mock) -> None:
        secrets = {randstr(): randstr().encode() for _ in range(randint(2, 5))}

        mock_get_config.return_value.secrets = {
            name: ConfigSecretBinary(binary=value) for name, value in secrets.items()
        }

        create_secrets()

        mock_get_client.assert_called_once_with('secretsmanager')
        assert mock_get_client.return_value.put_secret_value.call_count == len(secrets)
        for name, value in secrets.items():
            mock_get_client.return_value.put_secret_value.assert_any_call(SecretId=name, SecretBinary=value)
        mock_get_client.return_value.create_secret.assert_not_called()


class TestCreateTopics:
    @patch('qldebugger.actions.infra.get_client')
    @patch('qldebugger.actions.infra.get_config')
    def test_run(self, mock_get_config: Mock, mock_get_client: Mock) -> None:
        topics_names = [randstr() for _ in range(randint(2, 5))]

        mock_get_config.return_value.topics = {topic_name: ConfigTopic() for topic_name in topics_names}

        create_topics()

        mock_get_client.assert_called_once_with('sns')
        assert mock_get_client.return_value.create_topic.call_count == len(topics_names)
        for topic_name in topics_names:
            mock_get_client.return_value.create_topic.assert_any_call(Name=topic_name)


class TestCreateQueues:
    @patch('qldebugger.actions.infra.get_client')
    @patch('qldebugger.actions.infra.get_config')
    def test_create_queues(self, mock_get_config: Mock, mock_get_client: Mock) -> None:
        queues_names = [randstr() for _ in range(randint(2, 5))]

        mock_get_config.return_value.queues = {queue_name: ConfigQueue() for queue_name in queues_names}
        mock_get_client.return_value.get_queue_url.side_effect = ClientError({}, '')

        create_queues()

        mock_get_client.assert_called_once_with('sqs')
        assert mock_get_client.return_value.create_queue.call_count == len(queues_names)
        for queue_name in queues_names:
            mock_get_client.return_value.create_queue.assert_any_call(QueueName=queue_name, Attributes={})

    @patch('qldebugger.actions.infra.get_client')
    @patch('qldebugger.actions.infra.get_config')
    def test_update_queues(self, mock_get_config: Mock, mock_get_client: Mock) -> None:
        queues_names = [randstr() for _ in range(randint(2, 5))]
        host = randstr()

        mock_get_config.return_value.queues = {queue_name: ConfigQueue() for queue_name in queues_names}
        mock_get_client.return_value.get_queue_url.side_effect = lambda QueueName: {  # noqa: N803
            'QueueUrl': f'http://{host}/{QueueName}'
        }

        create_queues()

        mock_get_client.assert_called_once_with('sqs')
        assert mock_get_client.return_value.set_queue_attributes.call_count == len(queues_names)
        for queue_name in queues_names:
            mock_get_client.return_value.set_queue_attributes.assert_any_call(
                QueueUrl=f'http://{host}/{queue_name}', Attributes={}
            )

    @patch('qldebugger.actions.infra.get_client')
    @patch('qldebugger.actions.infra.get_config')
    def test_dead_letter_queue_should_created_first(self, mock_get_config: Mock, mock_get_client: Mock) -> None:
        a_max_receive_count = randint(1, 10)
        b_max_receive_count = randint(1, 10)
        queues = OrderedDict(
            [
                (
                    'b',
                    ConfigQueue(
                        redrive_policy=ConfigQueueRedrivePolicy(
                            dead_letter_queue='c', max_receive_count=b_max_receive_count
                        )
                    ),
                ),
                (
                    'a',
                    ConfigQueue(
                        redrive_policy=ConfigQueueRedrivePolicy(
                            dead_letter_queue='b', max_receive_count=a_max_receive_count
                        )
                    ),
                ),
                ('c', ConfigQueue()),
            ]
        )

        mock_get_config.return_value.queues = queues
        mock_get_client.return_value.get_queue_url.side_effect = ClientError({}, '')
        mock_get_client.return_value.get_queue_attributes.side_effect = lambda QueueUrl, AttributeNames: {  # noqa: N803
            'Attributes': {'QueueArn': f'arn:aws:sqs:us-east-1:123456789012:{QueueUrl}'}
        }

        create_queues()

        mock_get_client.assert_called_once_with('sqs')
        assert mock_get_client.return_value.create_queue.call_args_list == [
            call(QueueName='c', Attributes={}),
            call(
                QueueName='b',
                Attributes={
                    'RedrivePolicy': json.dumps(
                        {
                            'deadLetterTargetArn': 'arn:aws:sqs:us-east-1:123456789012:c',
                            'maxReceiveCount': b_max_receive_count,
                        }
                    )
                },
            ),
            call(
                QueueName='a',
                Attributes={
                    'RedrivePolicy': json.dumps(
                        {
                            'deadLetterTargetArn': 'arn:aws:sqs:us-east-1:123456789012:b',
                            'maxReceiveCount': a_max_receive_count,
                        }
                    )
                },
            ),
        ]

    @patch('qldebugger.actions.infra.get_client')
    @patch('qldebugger.actions.infra.get_config')
    def test_create_dead_letter_queue_not_in_queues(self, mock_get_config: Mock, mock_get_client: Mock) -> None:
        queue_name = randstr()
        dead_letter_queue = randstr()
        max_receive_count = randint(1, 10)

        mock_get_config.return_value.queues = {
            queue_name: ConfigQueue(
                redrive_policy=ConfigQueueRedrivePolicy(
                    dead_letter_queue=dead_letter_queue, max_receive_count=max_receive_count
                )
            )
        }
        mock_get_client.return_value.get_queue_url.side_effect = ClientError({}, '')
        mock_get_client.return_value.get_queue_attributes.side_effect = lambda QueueUrl, AttributeNames: {  # noqa: N803
            'Attributes': {'QueueArn': f'arn:aws:sqs:us-east-1:123456789012:{QueueUrl}'}
        }

        create_queues()

        mock_get_client.assert_called_once_with('sqs')
        assert mock_get_client.return_value.create_queue.call_args_list == [
            call(QueueName=dead_letter_queue, Attributes={}),
            call(
                QueueName=queue_name,
                Attributes={
                    'RedrivePolicy': json.dumps(
                        {
                            'deadLetterTargetArn': f'arn:aws:sqs:us-east-1:123456789012:{dead_letter_queue}',
                            'maxReceiveCount': max_receive_count,
                        }
                    )
                },
            ),
        ]

    @patch('qldebugger.actions.infra.get_client')
    @patch('qldebugger.actions.infra.get_config')
    def test_create_dead_letter_and_update_queue(self, mock_get_config: Mock, mock_get_client: Mock) -> None:
        queue_name = randstr()
        dead_letter_queue = randstr()
        max_receive_count = randint(1, 10)
        host = randstr()

        def get_queue_url(*, QueueName: str) -> Dict[str, str]:  # noqa: N803
            if QueueName != queue_name:
                raise ClientError({}, '')
            return {'QueueUrl': f'http://{host}/{QueueName}'}

        mock_get_config.return_value.queues = {
            queue_name: ConfigQueue(
                redrive_policy=ConfigQueueRedrivePolicy(
                    dead_letter_queue=dead_letter_queue, max_receive_count=max_receive_count
                )
            ),
            dead_letter_queue: ConfigQueue(),
        }
        mock_get_client.return_value.get_queue_url.side_effect = get_queue_url
        mock_get_client.return_value.get_queue_attributes.side_effect = lambda QueueUrl, AttributeNames: {  # noqa: N803
            'Attributes': {'QueueArn': f'arn:aws:sqs:us-east-1:123456789012:{QueueUrl}'}
        }

        create_queues()

        mock_get_client.assert_called_once_with('sqs')
        mock_get_client.return_value.create_queue.assert_called_once_with(QueueName=dead_letter_queue, Attributes={})
        mock_get_client.return_value.set_queue_attributes.assert_called_once_with(
            QueueUrl=f'http://{host}/{queue_name}',
            Attributes={
                'RedrivePolicy': json.dumps(
                    {
                        'deadLetterTargetArn': f'arn:aws:sqs:us-east-1:123456789012:{dead_letter_queue}',
                        'maxReceiveCount': max_receive_count,
                    }
                )
            },
        )


class TestSubscribeTopics:
    @patch('qldebugger.actions.infra.get_client')
    @patch('qldebugger.actions.infra.get_config')
    @patch('qldebugger.actions.infra.get_account_id')
    def test_topics_without_subscribers(
        self,
        mock_get_account_id: Mock,
        mock_get_config: Mock,
        mock_get_client: Mock,
    ) -> None:
        topics_names = [randstr() for _ in range(randint(2, 5))]

        mock_get_config.return_value.topics = {topic_name: ConfigTopic() for topic_name in topics_names}

        subscribe_topics()

        mock_get_client.assert_called_once_with('sns')
        mock_get_client.return_value.subscribe.assert_not_called()

    @patch('qldebugger.actions.infra.get_client')
    @patch('qldebugger.actions.infra.get_config')
    @patch('qldebugger.actions.infra.get_account_id')
    def test_topics_with_one_subscriber(
        self,
        mock_get_account_id: Mock,
        mock_get_config: Mock,
        mock_get_client: Mock,
    ) -> None:
        account_id = f'{randint(0, 999999999999):012}'
        region = randstr()
        topics_queues_names = [(randstr(), randstr()) for _ in range(randint(2, 5))]

        mock_get_account_id.return_value = account_id
        mock_get_config.return_value.topics = {
            topic_name: ConfigTopic(subscribers=[ConfigTopicSubscriber(queue=queue_name)])
            for topic_name, queue_name in topics_queues_names
        }
        mock_get_client.return_value.meta.region_name = region

        subscribe_topics()

        mock_get_client.assert_called_once_with('sns')
        assert mock_get_client.return_value.subscribe.call_count == len(topics_queues_names)
        for topic_name, queue_name in topics_queues_names:
            mock_get_client.return_value.subscribe.assert_any_call(
                TopicArn=f'arn:aws:sns:{region}:{account_id}:{topic_name}',
                Protocol='sqs',
                Endpoint=f'arn:aws:sqs:{region}:{account_id}:{queue_name}',
                Attributes={'RawMessageDelivery': 'false'},
            )

    @patch('qldebugger.actions.infra.get_client')
    @patch('qldebugger.actions.infra.get_config')
    @patch('qldebugger.actions.infra.get_account_id')
    def test_topic_with_multiple_subscribers(
        self,
        mock_get_account_id: Mock,
        mock_get_config: Mock,
        mock_get_client: Mock,
    ) -> None:
        account_id = f'{randint(0, 999999999999):012}'
        region = randstr()
        topic_name = randstr()
        queues_names = [randstr() for _ in range(randint(2, 5))]

        mock_get_account_id.return_value = account_id
        mock_get_config.return_value.topics = {
            topic_name: ConfigTopic(
                subscribers=[ConfigTopicSubscriber(queue=queue_name) for queue_name in queues_names],
            ),
        }
        mock_get_client.return_value.meta.region_name = region

        subscribe_topics()

        mock_get_client.assert_called_once_with('sns')
        assert mock_get_client.return_value.subscribe.call_count == len(queues_names)
        for queue_name in queues_names:
            mock_get_client.return_value.subscribe.assert_any_call(
                TopicArn=f'arn:aws:sns:{region}:{account_id}:{topic_name}',
                Protocol='sqs',
                Endpoint=f'arn:aws:sqs:{region}:{account_id}:{queue_name}',
                Attributes={'RawMessageDelivery': 'false'},
            )

    @patch('qldebugger.actions.infra.get_client')
    @patch('qldebugger.actions.infra.get_config')
    @patch('qldebugger.actions.infra.get_account_id')
    def test_raw_subscriber(
        self,
        mock_get_account_id: Mock,
        mock_get_config: Mock,
        mock_get_client: Mock,
    ) -> None:
        account_id = f'{randint(0, 999999999999):012}'
        region = randstr()
        topic_name = randstr()
        queue_name = randstr()

        mock_get_account_id.return_value = account_id
        mock_get_config.return_value.topics = {
            topic_name: ConfigTopic(
                subscribers=[ConfigTopicSubscriber(queue=queue_name, raw_message_delivery=True)],
            ),
        }
        mock_get_client.return_value.meta.region_name = region

        subscribe_topics()

        mock_get_client.assert_called_once_with('sns')
        mock_get_client.return_value.subscribe.assert_called_once_with(
            TopicArn=f'arn:aws:sns:{region}:{account_id}:{topic_name}',
            Protocol='sqs',
            Endpoint=f'arn:aws:sqs:{region}:{account_id}:{queue_name}',
            Attributes={'RawMessageDelivery': 'true'},
        )

    @patch('qldebugger.actions.infra.get_client')
    @patch('qldebugger.actions.infra.get_config')
    @patch('qldebugger.actions.infra.get_account_id')
    def test_subscriber_with_filter_policy(
        self,
        mock_get_account_id: Mock,
        mock_get_config: Mock,
        mock_get_client: Mock,
    ) -> None:
        account_id = f'{randint(0, 999999999999):012}'
        region = randstr()
        topic_name = randstr()
        queue_name = randstr()
        filter_policy = randstr()

        mock_get_account_id.return_value = account_id
        mock_get_config.return_value.topics = {
            topic_name: ConfigTopic(
                subscribers=[ConfigTopicSubscriber(queue=queue_name, filter_policy=filter_policy)],
            ),
        }
        mock_get_client.return_value.meta.region_name = region

        subscribe_topics()

        mock_get_client.assert_called_once_with('sns')
        mock_get_client.return_value.subscribe.assert_called_once_with(
            TopicArn=f'arn:aws:sns:{region}:{account_id}:{topic_name}',
            Protocol='sqs',
            Endpoint=f'arn:aws:sqs:{region}:{account_id}:{queue_name}',
            Attributes={'RawMessageDelivery': 'false', 'FilterPolicy': filter_policy},
        )

    @patch('qldebugger.actions.infra.get_client')
    @patch('qldebugger.actions.infra.get_config')
    @patch('qldebugger.actions.infra.get_account_id')
    def test_remove_old_subscribers(
        self,
        mock_get_account_id: Mock,
        mock_get_config: Mock,
        mock_get_client: Mock,
    ) -> None:
        subscriptions = [randstr() for _ in range(randint(2, 5))]

        mock_get_client.return_value.list_subscriptions.return_value = {
            'Subscriptions': [
                {'SubscriptionArn': subscription, 'Endpoint': randstr()} for subscription in subscriptions
            ]
        }

        subscribe_topics()

        mock_get_client.assert_called_once_with('sns')
        assert mock_get_client.return_value.unsubscribe.call_count == len(subscriptions)
        for subscription in subscriptions:
            mock_get_client.return_value.unsubscribe.assert_any_call(SubscriptionArn=subscription)
