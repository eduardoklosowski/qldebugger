from random import randint
from typing import TYPE_CHECKING, Any, cast
from unittest.mock import Mock, patch

import pytest

from qldebugger.actions.lambda_ import get_lambda_function, run_lambda
from qldebugger.config.file_parser import ConfigLambda
from tests.utils import randstr

if TYPE_CHECKING:
    from mypy_boto3_sqs.type_defs import ReceiveMessageResultTypeDef


class TestGetLambdaHandler:
    @patch('qldebugger.actions.lambda_.get_config')
    @patch('qldebugger.actions.lambda_.import_module')
    def test_success(self, mock_import_module: Mock, mock_get_config: Mock) -> None:
        lambda_name = randstr()
        module_name = randstr()
        function_name = randstr()

        mock_get_config.return_value.lambdas = {lambda_name: ConfigLambda(
            handler=f'{module_name}.{function_name}',
        )}

        returned = get_lambda_function(lambda_name=lambda_name)

        mock_import_module.assert_called_once_with(module_name)
        assert returned == getattr(mock_import_module.return_value, function_name)


class TestRunLambda:
    @patch('qldebugger.actions.lambda_.get_config')
    @patch('qldebugger.actions.lambda_.get_lambda_function')
    def test_run_lambda_with_success(
        self,
        mock_get_lambda_function: Mock,
        mock_get_config: Mock,
    ) -> None:
        lambda_name = randstr()
        event: 'ReceiveMessageResultTypeDef' = {
            'Messages': [
                {'MessageId': randstr(), 'ReceiptHandle': randstr(), 'Body': randstr()}
                for _ in range(randint(1, 10))
            ],
            'ResponseMetadata': cast(Any, None),
        }

        returned = run_lambda(lambda_name=lambda_name, event=event)

        mock_get_lambda_function.assert_called_once_with(lambda_name=lambda_name)
        mock_get_lambda_function.return_value.asser_called_once_with(event, None)
        assert returned == mock_get_lambda_function.return_value.return_value

    @patch('qldebugger.actions.lambda_.get_config')
    @patch('qldebugger.actions.lambda_.get_lambda_function')
    def test_run_lambda_with_error(
        self,
        mock_get_lambda_function: Mock,
        mock_get_config: Mock,
    ) -> None:
        lambda_name = randstr()
        event: 'ReceiveMessageResultTypeDef' = {
            'Messages': [
                {'MessageId': randstr(), 'ReceiptHandle': randstr(), 'Body': randstr()}
                for _ in range(randint(1, 10))
            ],
            'ResponseMetadata': cast(Any, None),
        }
        error = Exception(randstr())

        mock_get_lambda_function.return_value.side_effect = error

        with pytest.raises(Exception) as exc_info:
            run_lambda(lambda_name=lambda_name, event=event)

        mock_get_lambda_function.assert_called_once_with(lambda_name=lambda_name)
        mock_get_lambda_function.return_value.asser_called_once_with(event, None)
        assert exc_info.value == error

    @patch('qldebugger.actions.lambda_.get_config')
    @patch('qldebugger.actions.lambda_.get_lambda_function')
    def test_run_lambda_with_environment_variables(
        self,
        mock_get_lambda_function: Mock,
        mock_get_config: Mock,
    ) -> None:
        lambda_name = randstr()
        environment = {randstr(): randstr() for _ in range(randint(2, 5))}
        event: 'ReceiveMessageResultTypeDef' = {
            'Messages': [],
            'ResponseMetadata': cast(Any, None),
        }

        def lambda_function(event: 'ReceiveMessageResultTypeDef', context: None) -> None:
            import os
            for k, v in environment.items():
                assert os.environ[k] == v

        mock_get_config.return_value.lambdas = {lambda_name: ConfigLambda(handler='a.a', environment=environment)}
        mock_get_lambda_function.return_value = lambda_function

        run_lambda(lambda_name=lambda_name, event=event)
