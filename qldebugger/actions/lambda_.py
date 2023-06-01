import logging
from importlib import import_module
from traceback import format_exc
from typing import TYPE_CHECKING, Any, Callable
from unittest.mock import patch

from qldebugger.aws import inject_aws_config_in_client
from qldebugger.config import get_config

if TYPE_CHECKING:
    from aws_lambda_typing.events import SQSEvent

logger = logging.getLogger(__name__)


def get_lambda_function(*, lambda_name: str) -> Callable[['SQSEvent', None], Any]:
    module_name, function_name = get_config().lambdas[lambda_name].handler
    logger.debug('Importing lambda_handler of %r...', lambda_name)
    lambda_handler: Callable[['SQSEvent', None], Any] = \
        getattr(import_module(module_name), function_name)
    return lambda_handler


def run_lambda(*, lambda_name: str, event: 'SQSEvent') -> Any:
    environment = get_config().lambdas[lambda_name].environment
    with patch('boto3.client', inject_aws_config_in_client):
        lambda_handler = get_lambda_function(lambda_name=lambda_name)
        logger.info('Running %r lambda...', lambda_name)
        try:
            with patch.dict('os.environ', environment, True):
                result = lambda_handler(event, None)
        except Exception:
            logger.exception('Error on execute lambda:\n%s', format_exc())
            raise
        logger.info('Result: %r', result)
        return result
