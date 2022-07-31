from random import randint
from unittest.mock import Mock, patch

from qldebugger.actions.infra import create_queues
from qldebugger.config.file_parser import ConfigQueue
from tests.utils import randstr


class TestInfra:
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
