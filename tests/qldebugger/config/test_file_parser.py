from io import BytesIO
from random import randint
from typing import Any, ClassVar, Dict
from unittest.mock import Mock, patch

import pytest
from pydantic import ValidationError

from qldebugger.config.file_parser import (
    Config,
    ConfigAWS,
    ConfigEventSourceMapping,
    ConfigLambda,
    ConfigQueue,
    ConfigQueueRedrivePolicy,
    ConfigSecretBinary,
    ConfigSecretString,
    ConfigTopic,
    ConfigTopicSubscriber,
    NameHandlerTuple,
)
from tests.utils import randstr


class TestConfigAWS:
    def test_all_arguments_should_be_optional_and_none_default(self) -> None:
        returned = ConfigAWS()

        for v in returned.model_dump().values():
            assert v is None


class TestConfigSecretString:
    def test_get_value(self) -> None:
        value = randstr()

        sut = ConfigSecretString(string=value)
        returned = sut.get_value()

        assert returned == value


class TestConfigSecretBinary:
    def test_get_value(self) -> None:
        value = randstr().encode()

        sut = ConfigSecretBinary(binary=value)
        returned = sut.get_value()

        assert returned == value


class TestConfigTopicSubscriber:
    def test_default_values(self) -> None:
        queue_name = randstr()

        returned = ConfigTopicSubscriber(queue=queue_name)

        assert returned.model_dump() == {
            'queue': queue_name,
            'raw_message_delivery': False,
            'filter_policy': None,
        }


class TestConfigTopic:
    def test_default_values(self) -> None:
        returned = ConfigTopic()

        assert returned.model_dump() == {
            'subscribers': [],
        }


class TestConfigQueueRedrivePolicy:
    def test_required_fields(self) -> None:
        required_fields = ['dead_letter_queue', 'max_receive_count']

        with pytest.raises(ValidationError) as exc_info:
            ConfigQueueRedrivePolicy.model_validate({})

        assert {error['loc'] for error in exc_info.value.errors() if error['type'] == 'missing'} == {
            (field,) for field in required_fields
        }


class TestConfigQueue:
    def test_default_values(self) -> None:
        returned = ConfigQueue()

        assert returned.model_dump() == {
            'redrive_policy': None,
        }


class TestNameHandlerTuple:
    def test_tuple(self) -> None:
        module = randstr()
        function = randstr()

        returned = NameHandlerTuple(module, function)

        assert returned == (module, function)


class TestConfigLambda:
    DEFAULT_ARGS: ClassVar[Dict[str, Any]] = {
        'handler': f'{randstr()}.{randstr()}',
    }

    def test_default_values(self) -> None:
        returned = ConfigLambda(**self.DEFAULT_ARGS)

        assert returned.model_dump() == {
            'handler': tuple(self.DEFAULT_ARGS['handler'].rsplit('.', maxsplit=1)),
            'environment': {},
        }

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

        args = self.DEFAULT_ARGS.copy()
        args['handler'] = handler_name
        with pytest.raises(ValidationError) as exc_info:
            ConfigLambda(**args)

        errors = [error['loc'] for error in exc_info.value.errors() if error['type'] == 'value_error']
        assert ('handler',) in errors

    def test_handler_should_have_a_module_and_function_name(self) -> None:
        handler = randstr()

        args = self.DEFAULT_ARGS.copy()
        args['handler'] = handler
        with pytest.raises(ValidationError) as exc_info:
            ConfigLambda(**args)

        errors = [error['loc'] for error in exc_info.value.errors() if error['type'] == 'value_error']
        assert ('handler',) in errors

    def test_environment(self) -> None:
        args = self.DEFAULT_ARGS.copy()
        args['environment'] = {randstr(): randstr() for _ in range(randint(2, 5))}
        returned = ConfigLambda(**args)

        assert returned.environment == args['environment']


class TestConfigEventSourceMapping:
    DEFAULT_ARGS: ClassVar = {
        'queue': randstr(),
        'function_name': randstr(),
    }

    def test_default_values(self) -> None:
        returned = ConfigEventSourceMapping(**self.DEFAULT_ARGS)

        assert returned.model_dump() == {
            'queue': self.DEFAULT_ARGS['queue'],
            'function_name': self.DEFAULT_ARGS['function_name'],
            'batch_size': 10,
            'maximum_batching_window': 0,
        }


class TestConfig:
    def test_required_fields(self) -> None:
        required_fields = ['queues', 'lambdas', 'event_source_mapping']

        with pytest.raises(ValidationError) as exc_info:
            Config.model_validate({})

        assert len(required_fields) == len(exc_info.value.errors())
        errors = {error['loc'] for error in exc_info.value.errors() if error['type'] == 'missing'}
        for field in required_fields:
            assert (field,) in errors

    @patch('qldebugger.config.file_parser.tomli.load')
    def test_from_toml(self, mock_load: Mock) -> None:
        secret_name = randstr()
        topic_name = randstr()
        queue_name = randstr()
        lambda_name = randstr()
        event_source_mapping_name = randstr()

        fp = BytesIO(randstr().encode())

        mock_load.return_value = {
            'secrets': {
                secret_name: {'string': secret_name},
            },
            'topics': {
                topic_name: {},
            },
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
        assert returned.secrets.keys() == {secret_name}
        assert returned.topics.keys() == {topic_name}
        assert returned.queues.keys() == {queue_name}
        assert returned.lambdas.keys() == {lambda_name}
        assert returned.event_source_mapping.keys() == {event_source_mapping_name}
