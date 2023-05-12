from random import randint
from typing import TYPE_CHECKING, Any, cast
from unittest.mock import Mock, patch

import pytest

from qldebugger.actions.message import delete_messages, receive_message, send_message
from tests.utils import randstr

if TYPE_CHECKING:
    from mypy_boto3_sqs.type_defs import ReceiveMessageResultTypeDef


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
    def test_run_with_messages(self, mock_get_client: Mock) -> None:
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
    def test_run_without_messages(self, mock_get_client: Mock) -> None:
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
                {'MessageId': randstr(), 'ReceiptHandle': randstr(), 'Body': randstr()}
                for _ in range(randint(1, 10))
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
                } for message in messages['Messages']
            ],
        )
