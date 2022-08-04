from random import randint
from typing import TYPE_CHECKING, Any, cast
from unittest.mock import Mock, patch

import pytest

from qldebugger.example.lambdas import exec_fail, print_messages
from tests.utils import randstr

if TYPE_CHECKING:
    from mypy_boto3_sqs.type_defs import ReceiveMessageResultTypeDef


class TestPrintMessages:
    @patch('qldebugger.example.lambdas.print')
    def test_run(self, mock_print: Mock) -> None:
        event: ReceiveMessageResultTypeDef = {
            'Messages': [{'Body': randstr()} for _ in range(randint(2, 10))],
            'ResponseMetadata': cast(Any, None),
        }

        print_messages(event, None)

        assert mock_print.call_count == len(event['Messages']) + 1
        for message in event['Messages']:
            mock_print.assert_any_call(message['Body'])
        mock_print.assert_any_call(f'Total: {len(event["Messages"])} messages')


class TestExecFail:
    def test_run(self) -> None:
        event: ReceiveMessageResultTypeDef = {
            'Messages': [],
            'ResponseMetadata': cast(Any, None),
        }

        with pytest.raises(Exception) as exc_info:
            exec_fail(event, None)

        assert exc_info.value.args[0] == 'Lambda execution fail'
