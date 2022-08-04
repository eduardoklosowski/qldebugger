import logging
from importlib import import_module
from traceback import format_exc
from typing import TYPE_CHECKING, Any, Callable
from unittest.mock import patch

from qldebugger.aws import inject_aws_config_in_client

from ..config import get_config

if TYPE_CHECKING:
    from mypy_boto3_sqs.type_defs import ReceiveMessageResultTypeDef

logger = logging.getLogger(__name__)


def get_lambda_function(*, lambda_name: str) -> Callable[['ReceiveMessageResultTypeDef', None], Any]:
    logger.debug('Importing lambda_handler of %r...', lambda_name)
    module_name, function_name = get_config().lambdas[lambda_name].handler
    lambda_handler: Callable[['ReceiveMessageResultTypeDef', None], Any] = \
        getattr(import_module(module_name), function_name)
    return lambda_handler


def run_lambda(*, lambda_name: str, event: 'ReceiveMessageResultTypeDef') -> Any:
    environment = get_config().lambdas[lambda_name].environment
    with patch('boto3.client', inject_aws_config_in_client):
        lambda_handler = get_lambda_function(lambda_name=lambda_name)
        logger.info('Running %r lambda...', lambda_name)
        try:
            with patch.dict('os.environ', environment, True):
                result = lambda_handler(event, None)
            logger.info('Result: %r', result)
            return result
        except Exception:
            logger.error('Error on execute lambda:\n%s', format_exc())
            raise
