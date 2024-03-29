from unittest.mock import Mock, patch

import pytest

from qldebugger.config import get_config, load_config
from tests.utils import randstr


class TestLoadConfig:
    @patch('qldebugger.config.Path')
    @patch('qldebugger.config.Config')
    def test_load_config(self, mock_config: Mock, mock_path: Mock) -> None:
        filename = randstr()

        returned = load_config(filename)

        mock_path.assert_called_once_with(filename)
        mock_path.return_value.open.assert_called_once_with('rb')
        mock_config.from_toml.assert_called_once_with(mock_path.return_value.open.return_value.__enter__.return_value)
        assert returned == mock_config.from_toml.return_value


class TestGetConfig:
    @patch('qldebugger.config._current_config', None)
    def test_get_config_without_load_first(self) -> None:
        with pytest.raises(RuntimeError, match='Configuration file is not loaded yet'):
            get_config()

    @patch('qldebugger.config._current_config')
    def test_get_config_after_load(self, mock_current_config: Mock) -> None:
        returned = get_config()

        assert returned == mock_current_config
