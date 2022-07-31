import logging
from functools import lru_cache
from typing import TYPE_CHECKING, Literal

import boto3

from .config import get_config

if TYPE_CHECKING:
    from mypy_boto3_sqs import SQSClient

logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def get_client(service_name: Literal['sqs'], /) -> 'SQSClient':
    aws_config = get_config().aws
    logger.debug('Connecting to %s service...', service_name)
    session = boto3.Session(
        aws_access_key_id=aws_config.access_key_id,
        aws_secret_access_key=aws_config.secret_access_key,
        aws_session_token=aws_config.session_token,
        region_name=aws_config.region,
        profile_name=aws_config.profile,
    )
    return session.client(
        service_name=service_name,
        endpoint_url=aws_config.endpoint_url,
    )
