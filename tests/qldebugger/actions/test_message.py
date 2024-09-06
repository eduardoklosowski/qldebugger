from random import randint
from typing import TYPE_CHECKING, Any, Mapping, cast
from unittest.mock import Mock, patch

import pytest

from qldebugger.actions.message import delete_messages, publish_message, purge_messages, receive_message, send_message
from tests.utils import randstr

if TYPE_CHECKING:
    from mypy_boto3_sns.type_defs import MessageAttributeValueTypeDef
    from mypy_boto3_sqs.type_defs import ReceiveMessageResultTypeDef


class TestPublishMessage:
    @patch('qldebugger.actions.message.get_account_id')
    @patch('qldebugger.actions.message.get_client')
    def test_without_attributes(self, mock_get_client: Mock, mock_get_account_id: Mock) -> None:
        account_id = f'{randint(0, 999999999999):012}'
        region = randstr()
        topic_name = randstr()
        message = randstr()

        mock_get_account_id.return_value = account_id
        mock_get_client.return_value.meta.region_name = region

        publish_message(topic_name=topic_name, message=message)

        mock_get_client.assert_called_once_with('sns')
        mock_get_client.return_value.publish(
            TopicArn=f'arn:aws:sns:{region}:{account_id}:{topic_name}',
            Message=message,
            MessageAttributes={},
        )

    @patch('qldebugger.actions.message.get_account_id')
    @patch('qldebugger.actions.message.get_client')
    def test_with_attributes(self, mock_get_client: Mock, mock_get_account_id: Mock) -> None:
        account_id = f'{randint(0, 999999999999):012}'
        region = randstr()
        topic_name = randstr()
        message = randstr()
        attributes = cast(
            Mapping[str, 'MessageAttributeValueTypeDef'],
            {randstr(): {'DataType': 'String', 'StringValue': randstr()} for _ in range(randint(2, 5))},
        )

        mock_get_account_id.return_value = account_id
        mock_get_client.return_value.meta.region_name = region

        publish_message(topic_name=topic_name, message=message, attributes=attributes)

        mock_get_client.assert_called_once_with('sns')
        mock_get_client.return_value.publish(
            TopicArn=f'arn:aws:sns:{region}:{account_id}:{topic_name}',
            Message=message,
            MessageAttributes=attributes,
        )


class TestSendMessage:
    @patch('qldebugger.actions.message.get_client')
    def test_run(self, mock_get_client: Mock) -> None:
        queue_name = randstr()
        queue_url = randstr()
        message = randstr()

        mock_get_client.return_value.get_queue_url.return_value = {'QueueUrl': queue_url}

        send_message(queue_name=queue_name, message=message)

        mock_get_client.assert_called_once_with('sqs')
        mock_get_client.return_value.get_queue_url.assert_called_once_with(QueueName=queue_name)
        mock_get_client.return_value.send_message.assert_called_once_with(QueueUrl=queue_url, MessageBody=message)


class TestReceiveMessage:
    @patch('qldebugger.actions.message.get_client')
    def test_with_messages_in_queue(self, mock_get_client: Mock) -> None:
        queue_name = randstr()
        queue_url = randstr()
        batch_size = randint(1, 10)
        maximum_batching_window = randint(0, 30)

        mock_get_client.return_value.get_queue_url.return_value = {'QueueUrl': queue_url}
        mock_get_client.return_value.receive_message.return_value = {
            'Messages': [randstr(10) for _ in range(randint(2, 5))],
        }

        returned = receive_message(
            queue_name=queue_name,
            batch_size=batch_size,
            maximum_batching_window=maximum_batching_window,
        )

        mock_get_client.assert_called_once_with('sqs')
        mock_get_client.return_value.get_queue_url.assert_called_once_with(QueueName=queue_name)
        mock_get_client.return_value.receive_message.assert_called_once_with(
            QueueUrl=queue_url,
            MaxNumberOfMessages=batch_size,
            WaitTimeSeconds=maximum_batching_window,
        )
        assert returned == mock_get_client.return_value.receive_message.return_value

    @patch('qldebugger.actions.message.get_client')
    def test_without_messages_in_queue(self, mock_get_client: Mock) -> None:
        queue_name = randstr()
        queue_url = randstr()
        batch_size = randint(1, 10)
        maximum_batching_window = randint(0, 30)

        mock_get_client.return_value.get_queue_url.return_value = {'QueueUrl': queue_url}
        mock_get_client.return_value.receive_message.return_value = {}

        with pytest.raises(RuntimeWarning, match='No messages received'):
            receive_message(
                queue_name=queue_name,
                batch_size=batch_size,
                maximum_batching_window=maximum_batching_window,
            )

        mock_get_client.assert_called_once_with('sqs')
        mock_get_client.return_value.get_queue_url.assert_called_once_with(QueueName=queue_name)
        mock_get_client.return_value.receive_message.assert_called_once_with(
            QueueUrl=queue_url,
            MaxNumberOfMessages=batch_size,
            WaitTimeSeconds=maximum_batching_window,
        )


class TestDeleteMessages:
    @patch('qldebugger.actions.message.get_client')
    def test_run(self, mock_get_client: Mock) -> None:
        queue_name = randstr()
        queue_url = randstr()
        messages: 'ReceiveMessageResultTypeDef' = {
            'Messages': [
                {'MessageId': randstr(), 'ReceiptHandle': randstr(), 'Body': randstr()} for _ in range(randint(1, 10))
            ],
            'ResponseMetadata': cast(Any, None),
        }

        mock_get_client.return_value.get_queue_url.return_value = {'QueueUrl': queue_url}

        delete_messages(queue_name=queue_name, messages=messages)

        mock_get_client.assert_called_once_with('sqs')
        mock_get_client.return_value.get_queue_url.assert_called_once_with(QueueName=queue_name)
        mock_get_client.return_value.delete_message_batch.assert_called_once_with(
            QueueUrl=queue_url,
            Entries=[
                {
                    'Id': message['MessageId'],
                    'ReceiptHandle': message['ReceiptHandle'],
                }
                for message in messages['Messages']
            ],
        )


class TestPurgeMessages:
    @patch('qldebugger.actions.message.get_client')
    def test_run(self, mock_get_client: Mock) -> None:
        queue_name = randstr()
        queue_url = randstr()

        mock_get_client.return_value.get_queue_url.return_value = {'QueueUrl': queue_url}

        purge_messages(queue_name=queue_name)

        mock_get_client.assert_called_once_with('sqs')
        mock_get_client.return_value.get_queue_url.assert_called_once_with(QueueName=queue_name)
        mock_get_client.return_value.purge_queue.assert_called_once_with(QueueUrl=queue_url)
