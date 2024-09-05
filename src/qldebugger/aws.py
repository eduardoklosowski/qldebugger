import logging
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Literal, Optional, Union, overload

import boto3
from botocore.config import Config

from .config import get_config

if TYPE_CHECKING:
    from mypy_boto3_secretsmanager import SecretsManagerClient
    from mypy_boto3_sns import SNSClient
    from mypy_boto3_sqs import SQSClient
    from mypy_boto3_sts import STSClient

logger = logging.getLogger(__name__)


@overload
def get_client(service_name: Literal['secretsmanager'], /) -> 'SecretsManagerClient': ...


@overload
def get_client(service_name: Literal['sns'], /) -> 'SNSClient': ...


@overload
def get_client(service_name: Literal['sqs'], /) -> 'SQSClient': ...


@overload
def get_client(service_name: Literal['sts'], /) -> 'STSClient': ...


def get_client(service_name, /):  # type: ignore[no-untyped-def]
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


get_client = lru_cache(maxsize=None)(get_client)  # type: ignore[assignment]


def get_account_id() -> str:
    sts = get_client('sts')
    return sts.get_caller_identity()['Account']


def inject_aws_config_in_client(
    service_name: str,
    region_name: Optional[str] = None,
    api_version: Optional[str] = None,
    use_ssl: Optional[bool] = True,
    verify: Optional[Union[bool, str]] = None,
    endpoint_url: Optional[str] = None,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    config: Optional[Config] = None,
) -> Any:
    aws_config = get_config().aws
    if aws_config.access_key_id is not None:
        aws_access_key_id = aws_config.access_key_id
    if aws_config.secret_access_key is not None:
        aws_secret_access_key = aws_config.secret_access_key
    if aws_config.session_token is not None:
        aws_session_token = aws_config.session_token
    if aws_config.region is not None:
        region_name = aws_config.region
    if aws_config.endpoint_url is not None:
        endpoint_url = aws_config.endpoint_url
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        region_name=region_name,
        profile_name=aws_config.profile,
    )
    return session.client(  # type: ignore[call-overload,misc]
        service_name=service_name,
        api_version=api_version,
        use_ssl=use_ssl,
        verify=verify,
        endpoint_url=endpoint_url,
        config=config,
    )
