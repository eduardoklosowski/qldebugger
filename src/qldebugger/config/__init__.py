import logging
from pathlib import Path
from typing import Optional, Union

from .file_parser import Config

logger = logging.getLogger(__name__)

_current_config: Optional[Config] = None


def load_config(filename: Union[str, Path], /) -> Config:
    logger.debug('Loading %r config...', str(filename))
    global _current_config  # noqa: PLW0603
    with Path(filename).open('rb') as fp:
        _current_config = Config.from_toml(fp)
    return _current_config


def get_config() -> Config:
    if _current_config is None:
        raise RuntimeError('Configuration file is not loaded yet')
    return _current_config
