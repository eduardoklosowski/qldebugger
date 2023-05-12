from random import randint
from typing import Any
from unittest.mock import Mock, patch

import pytest

from qldebugger.example.lambdas import exec_fail, print_messages
from tests.utils import randstr


class TestPrintMessages:
    @patch('qldebugger.example.lambdas.print')
    def test_run(self, mock_print: Mock) -> None:
        event: Any = {
            'Records': [{'body': randstr()} for _ in range(randint(2, 10))],
        }

        print_messages(event, None)

        assert mock_print.call_count == len(event['Records']) + 1
        for message in event['Records']:
            mock_print.assert_any_call(message['body'])
        mock_print.assert_any_call(f'Total: {len(event["Records"])} messages')


class TestExecFail:
    def test_run(self) -> None:
        event: Any = {}

        with pytest.raises(Exception, match='Lambda execution fail'):
            exec_fail(event, None)
