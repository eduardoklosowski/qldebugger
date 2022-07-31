from unittest.mock import Mock, patch

from qldebugger.actions.message import send_message
from tests.utils import randstr


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
