from random import randint
from unittest.mock import Mock, patch

from botocore.exceptions import ClientError
from qldebugger.actions.infra import create_queues, create_secrets, create_topics, subscribe_topics
from qldebugger.config.file_parser import (
    ConfigQueue,
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
            name: ConfigSecretString(string=value)
            for name, value in secrets.items()
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
            name: ConfigSecretBinary(binary=value)
            for name, value in secrets.items()
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
            name: ConfigSecretString(string=value)
            for name, value in secrets.items()
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
            name: ConfigSecretBinary(binary=value)
            for name, value in secrets.items()
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
    def test_run(self, mock_get_config: Mock, mock_get_client: Mock) -> None:
        queues_names = [randstr() for _ in range(randint(2, 5))]

        mock_get_config.return_value.queues = {queue_name: ConfigQueue() for queue_name in queues_names}

        create_queues()

        mock_get_client.assert_called_once_with('sqs')
        assert mock_get_client.return_value.create_queue.call_count == len(queues_names)
        for queue_name in queues_names:
            mock_get_client.return_value.create_queue.assert_any_call(QueueName=queue_name)


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

        mock_get_client.return_value.list_subscriptions.return_value = {'Subscriptions': [
            {'SubscriptionArn': subscription, 'Endpoint': randstr()}
            for subscription in subscriptions
        ]}

        subscribe_topics()

        mock_get_client.assert_called_once_with('sns')
        assert mock_get_client.return_value.unsubscribe.call_count == len(subscriptions)
        for subscription in subscriptions:
            mock_get_client.return_value.unsubscribe.assert_any_call(SubscriptionArn=subscription)
