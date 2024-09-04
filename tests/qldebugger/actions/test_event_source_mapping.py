from random import randint
from typing import TYPE_CHECKING, Any, cast
from unittest.mock import Mock, patch

from qldebugger.actions.event_source_mapping import convert_sqs_messages_to_event, receive_messages_and_run_lambda
from qldebugger.config.file_parser import ConfigEventSourceMapping

from tests.utils import randstr

if TYPE_CHECKING:
    from mypy_boto3_sqs.type_defs import ReceiveMessageResultTypeDef


class TestReceiveMessagesAndRunLambda:
    @patch('qldebugger.actions.event_source_mapping.get_account_id')
    @patch('qldebugger.actions.event_source_mapping.get_client')
    @patch('qldebugger.actions.event_source_mapping.get_config')
    @patch('qldebugger.actions.event_source_mapping.receive_message')
    @patch('qldebugger.actions.event_source_mapping.convert_sqs_messages_to_event')
    @patch('qldebugger.actions.event_source_mapping.run_lambda')
    @patch('qldebugger.actions.event_source_mapping.delete_messages')
    def test_run(
        self,
        mock_delete_messages: Mock,
        mock_run_lambda: Mock,
        mock_convert_sqs_messages_to_event: Mock,
        mock_receive_message: Mock,
        mock_get_config: Mock,
        mock_get_client: Mock,
        mock_get_account_id: Mock,
    ) -> None:
        partition = randstr()
        aws_region = randstr()
        event_source_mapping_name = randstr()
        account_id = randint(100000000000, 999999999999)
        queue_name = randstr()
        queue_arn = f'arn:{partition}:sqs:{aws_region}:{account_id}:{queue_name}'
        batch_size = randint(1, 10)
        maximum_batching_window = randint(0, 20)
        lambda_name = randstr()

        mock_get_account_id.return_value = account_id
        mock_get_client.return_value.meta.partition = partition
        mock_get_client.return_value.meta.region_name = aws_region
        mock_get_config.return_value.event_source_mapping = {
            event_source_mapping_name: ConfigEventSourceMapping(
                queue=queue_name,
                batch_size=batch_size,
                maximum_batching_window=maximum_batching_window,
                function_name=lambda_name,
            ),
        }

        receive_messages_and_run_lambda(event_source_mapping_name=event_source_mapping_name)

        mock_receive_message.assert_called_once_with(
            queue_name=queue_name,
            batch_size=batch_size,
            maximum_batching_window=maximum_batching_window,
        )
        mock_convert_sqs_messages_to_event.assert_called_once_with(
            aws_region=aws_region,
            event_source=f'{partition}:sqs',
            event_source_arn=queue_arn,
            messages=mock_receive_message.return_value,
        )
        mock_run_lambda.assert_called_once_with(
            lambda_name=lambda_name,
            event=mock_convert_sqs_messages_to_event.return_value,
        )
        mock_delete_messages.assert_called_once_with(
            queue_name=queue_name,
            messages=mock_receive_message.return_value,
        )


class TestConvertSqsMessagesToEvent:
    def test_run(self) -> None:
        aws_region = randstr()
        event_source = randstr()
        event_source_arn = randstr()
        messages: 'ReceiveMessageResultTypeDef' = {
            'Messages': [
                {
                    'MessageId': randstr(),
                    'ReceiptHandle': randstr(),
                    'Body': randstr(),
                    'Attributes': {},
                    'MessageAttributes': {},
                    'MD5OfBody': randstr(),
                }
                for _ in range(randint(2, 5))
            ],
            'ResponseMetadata': cast(Any, None),
        }

        returned = convert_sqs_messages_to_event(
            aws_region=aws_region,
            event_source=event_source,
            event_source_arn=event_source_arn,
            messages=messages,
        )

        assert returned == {
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
