from unittest.mock import Mock, patch

from qldebugger.aws import get_client
from qldebugger.config.file_parser import ConfigAWS
from tests.utils import randstr


class TestGetClient:
    @patch('qldebugger.aws.get_config')
    @patch('qldebugger.aws.boto3')
    def test_get_sqs_client(self, mock_boto3: Mock, mock_get_config: Mock) -> None:
        aws_config = ConfigAWS(
            profile=randstr(),
            access_key_id=randstr(),
            secret_access_key=randstr(),
            session_token=randstr(),
            region=randstr(),
            endpoint_url=randstr(),
        )

        mock_get_config.return_value.aws = aws_config

        returned = get_client('sqs')

        mock_boto3.Session.assert_called_once_with(
            aws_access_key_id=aws_config.access_key_id,
            aws_secret_access_key=aws_config.secret_access_key,
            aws_session_token=aws_config.session_token,
            region_name=aws_config.region,
            profile_name=aws_config.profile,
        )
        mock_boto3.Session.return_value.client.assert_called_once_with(
            service_name='sqs',
            endpoint_url=aws_config.endpoint_url,
        )
        assert returned == mock_boto3.Session.return_value.client.return_value
