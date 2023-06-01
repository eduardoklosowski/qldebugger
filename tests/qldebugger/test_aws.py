from random import randint
from unittest.mock import Mock, patch

import pytest

from qldebugger.aws import get_account_id, get_client, inject_aws_config_in_client
from qldebugger.config.file_parser import ConfigAWS
from tests.utils import randstr


class TestGetClient:
    @pytest.mark.parametrize('service', ['sns', 'sqs', 'sts'])
    @patch('qldebugger.aws.get_config')
    @patch('qldebugger.aws.boto3')
    def test_run(self, mock_boto3: Mock, mock_get_config: Mock, service: str) -> None:
        aws_config = ConfigAWS(
            profile=randstr(),
            access_key_id=randstr(),
            secret_access_key=randstr(),
            session_token=randstr(),
            region=randstr(),
            endpoint_url=randstr(),
        )

        mock_get_config.return_value.aws = aws_config

        returned = get_client(service)  # type: ignore[call-overload]

        mock_boto3.Session.assert_called_once_with(
            aws_access_key_id=aws_config.access_key_id,
            aws_secret_access_key=aws_config.secret_access_key,
            aws_session_token=aws_config.session_token,
            region_name=aws_config.region,
            profile_name=aws_config.profile,
        )
        mock_boto3.Session.return_value.client.assert_called_once_with(
            service_name=service,
            endpoint_url=aws_config.endpoint_url,
        )
        assert returned == mock_boto3.Session.return_value.client.return_value

    @patch('qldebugger.aws.get_config')
    @patch('qldebugger.aws.boto3')
    def test_cache(self, mock_boto3: Mock, mock_get_config: Mock) -> None:
        aws_config = ConfigAWS(
            profile=randstr(),
            access_key_id=randstr(),
            secret_access_key=randstr(),
            session_token=randstr(),
            region=randstr(),
            endpoint_url=randstr(),
        )

        mock_get_config.return_value.aws = aws_config
        mock_boto3.Session.return_value.client.side_effect = lambda **kwargs: object()

        get_client.cache_clear()  # type: ignore[attr-defined]

        returned1 = get_client('sts')

        cache_info = get_client.cache_info()  # type: ignore[attr-defined]
        assert cache_info.hits == 0
        assert cache_info.misses == 1
        assert mock_boto3.Session.call_count == 1
        assert mock_boto3.Session.return_value.client.call_count == 1

        returned2 = get_client('sts')

        cache_info = get_client.cache_info()  # type: ignore[attr-defined]
        assert cache_info.hits == 1
        assert cache_info.misses == 1
        assert mock_boto3.Session.call_count == 1
        assert mock_boto3.Session.return_value.client.call_count == 1
        assert returned1 is returned2

        returned3 = get_client('sqs')

        cache_info = get_client.cache_info()  # type: ignore[attr-defined]
        assert cache_info.hits == 1
        assert cache_info.misses == 2
        assert mock_boto3.Session.call_count == 2
        assert mock_boto3.Session.return_value.client.call_count == 2
        assert returned3 is not returned1  # type: ignore[comparison-overlap]


class TestGetAccountId:
    @patch('qldebugger.aws.get_client')
    def test_run(self, mock_get_client: Mock) -> None:
        account_id = f'{randint(0, 999999999999):012}'

        mock_get_client.return_value.get_caller_identity.return_value = {
            'Account': account_id,
        }

        returned = get_account_id()

        mock_get_client.assert_called_once_with('sts')
        mock_get_client.return_value.get_caller_identity.assert_called_once_with()
        assert returned == account_id


class TestInjectAwsConfigInClient:
    @patch('qldebugger.aws.get_config')
    @patch('qldebugger.aws.boto3')
    def test_without_aws_configuration(self, mock_boto3: Mock, mock_get_config: Mock) -> None:
        service_name = randstr()

        mock_get_config.return_value.aws = ConfigAWS()

        inject_aws_config_in_client(service_name)

        mock_boto3.Session.assert_called_once_with(
            aws_access_key_id=None,
            aws_secret_access_key=None,
            aws_session_token=None,
            region_name=None,
            profile_name=None,
        )
        mock_boto3.Session.return_value.client.assert_called_once_with(
            service_name=service_name,
            api_version=None,
            use_ssl=True,
            verify=None,
            endpoint_url=None,
            config=None,
        )

    @patch('qldebugger.aws.get_config')
    @patch('qldebugger.aws.boto3')
    def test_with_aws_configuration(self, mock_boto3: Mock, mock_get_config: Mock) -> None:
        service_name = randstr()
        config = ConfigAWS(
            profile=randstr(),
            access_key_id=randstr(),
            secret_access_key=randstr(),
            session_token=randstr(),
            region=randstr(),
            endpoint_url=f'https://{randstr()}',
        )

        mock_get_config.return_value.aws = config

        inject_aws_config_in_client(service_name)

        mock_boto3.Session.assert_called_once_with(
            aws_access_key_id=config.access_key_id,
            aws_secret_access_key=config.secret_access_key,
            aws_session_token=config.session_token,
            region_name=config.region,
            profile_name=config.profile,
        )
        mock_boto3.Session.return_value.client.assert_called_once_with(
            service_name=service_name,
            api_version=None,
            use_ssl=True,
            verify=None,
            endpoint_url=config.endpoint_url,
            config=None,
        )
