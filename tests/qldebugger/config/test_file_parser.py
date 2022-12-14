from io import BytesIO
from random import randint
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest
from pydantic import ValidationError

from qldebugger.config.file_parser import Config, ConfigAWS, ConfigEventSourceMapping, ConfigLambda, ConfigQueue
from tests.utils import randstr


class TestConfigAWS:
    def test_all_arguments_should_be_optional_and_none_default(self) -> None:
        returned = ConfigAWS()

        for k, v in returned.dict().items():
            assert v is None


class TestConfigQueue:
    def test_empty_object(self) -> None:
        returned = ConfigQueue()

        assert returned.dict() == {}


class TestConfigLambda:
    DEFAULT_ARGS: Dict[str, Any] = {
        'handler': f'{randstr()}.{randstr()}',
    }

    def test_default_values(self) -> None:
        returned = ConfigLambda(**self.DEFAULT_ARGS)

        assert returned.environment == {}

    def test_handler_argument(self) -> None:
        module_name = '.'.join(randstr() for _ in range(randint(3, 10)))
        function_name = randstr()
        handler_name = f'{module_name}.{function_name}'

        args = self.DEFAULT_ARGS.copy()
        args['handler'] = handler_name
        returned = ConfigLambda(**args)

        assert returned.handler == (module_name, function_name)
        assert returned.handler.module == module_name
        assert returned.handler.function == function_name

    def test_hander_should_raise_erro_on_receive_non_str(self) -> None:
        handler_name = randint(0, 99)

        with pytest.raises(ValidationError) as exc_info:
            args = self.DEFAULT_ARGS.copy()
            args['handler'] = handler_name
            ConfigLambda(**args)

        assert {
            'type': 'value_error',
            'loc': tuple(['handler']),
            'msg': 'should be a str',
        } in exc_info.value.errors()

    def test_handler_should_have_a_module_and_function_name(self) -> None:
        handler = randstr()

        with pytest.raises(ValidationError) as exc_info:
            args = self.DEFAULT_ARGS.copy()
            args['handler'] = handler
            ConfigLambda(**args)

        assert {
            'type': 'value_error',
            'loc': tuple(['handler']),
            'msg': 'should have a module and function names',
        } in exc_info.value.errors()

    def test_environment(self) -> None:
        args = self.DEFAULT_ARGS.copy()
        args['environment'] = {randstr(): randstr() for _ in range(randint(2, 5))}
        returned = ConfigLambda(**args)

        assert returned.environment == args['environment']


class TestConfigEventSourceMapping:
    DEFAULT_ARGS = {
        'queue': randstr(),
        'function_name': randstr(),
    }

    def test_default_values(self) -> None:
        returned = ConfigEventSourceMapping(**self.DEFAULT_ARGS)

        assert returned.batch_size == 10
        assert returned.maximum_batching_window == 0


class TestConfig:
    def test_required_fields(self) -> None:
        required_fields = ['queues', 'lambdas', 'event_source_mapping']

        with pytest.raises(ValidationError) as exc_info:
            Config.parse_obj({})

        assert len(required_fields) == len(exc_info.value.errors())
        for field in required_fields:
            assert {
                'type': 'value_error.missing',
                'loc': tuple([field]),
                'msg': 'field required',
            } in exc_info.value.errors()

    @patch('qldebugger.config.file_parser.tomli.load')
    def test_from_toml(self, mock_load: Mock) -> None:
        queue_name = randstr()
        lambda_name = randstr()
        event_source_mapping_name = randstr()

        fp = BytesIO(randstr().encode())

        mock_load.return_value = {
            'queues': {
                queue_name: {},
            },
            'lambdas': {
                lambda_name: {'handler': 'aaa.bbb'},
            },
            'event_source_mapping': {
                event_source_mapping_name: {'queue': queue_name, 'function_name': lambda_name},
            },
        }

        returned = Config.from_toml(fp)

        mock_load.assert_called_once_with(fp)
        assert returned.queues.keys() == {queue_name}
        assert returned.lambdas.keys() == {lambda_name}
        assert returned.event_source_mapping.keys() == {event_source_mapping_name}
