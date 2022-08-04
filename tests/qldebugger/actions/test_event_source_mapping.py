from random import randint
from unittest.mock import Mock, patch

from qldebugger.actions.event_source_mapping import receive_messages_and_run_lambda
from qldebugger.config.file_parser import ConfigEventSourceMapping
from tests.utils import randstr


class TestReceiveMessagesAndRunLambda:
    @patch('qldebugger.actions.event_source_mapping.get_config')
    @patch('qldebugger.actions.event_source_mapping.receive_message')
    @patch('qldebugger.actions.event_source_mapping.run_lambda')
    @patch('qldebugger.actions.event_source_mapping.delete_messages')
    def test_run(
        self,
        mock_delete_messages: Mock,
        mock_run_lambda: Mock,
        mock_receive_message: Mock,
        mock_get_config: Mock,
    ) -> None:
        event_source_mapping_name = randstr()
        queue_name = randstr()
        batch_size = randint(1, 10)
        maximum_batching_window = randint(0, 30)
        lambda_name = randstr()

        mock_get_config.return_value.event_source_mapping = {
            event_source_mapping_name: ConfigEventSourceMapping(
                queue=queue_name,
                batch_size=batch_size,
                maximum_batching_window=maximum_batching_window,
                function_name=lambda_name,
            )
        }

        receive_messages_and_run_lambda(event_source_mapping_name=event_source_mapping_name)

        mock_receive_message.assert_called_once_with(
            queue_name=queue_name,
            batch_size=batch_size,
            maximum_batching_window=maximum_batching_window,
        )
        mock_run_lambda.assert_called_once_with(lambda_name=lambda_name, event=mock_receive_message.return_value)
        mock_delete_messages.assert_called_once_with(queue_name=queue_name, messages=mock_receive_message.return_value)
