from abc import ABC, abstractmethod
from typing import Any, BinaryIO, Dict, List, NamedTuple, Optional, Tuple, Union

import tomli
from pydantic import BaseModel, Field, validator


class ConfigAWS(BaseModel):
    profile: Optional[str]
    access_key_id: Optional[str]
    secret_access_key: Optional[str]
    session_token: Optional[str]
    region: Optional[str]
    endpoint_url: Optional[str]


class ConfigSecret(BaseModel, ABC):
    @abstractmethod
    def get_value(self) -> Union[str, bytes]:
        ...


class ConfigSecretString(ConfigSecret):
    string: str

    def get_value(self) -> str:
        return self.string


class ConfigSecretBinary(ConfigSecret):
    binary: bytes

    def get_value(self) -> bytes:
        return self.binary


class ConfigTopicSubscriber(BaseModel):
    queue: str
    raw_message_delivery: bool = False
    filter_policy: Optional[str] = None


class ConfigTopic(BaseModel):
    subscribers: List[ConfigTopicSubscriber] = Field(default_factory=list)


class ConfigQueue(BaseModel):
    ...


class NameHandlerTuple(NamedTuple):
    module: str
    function: str


class ConfigLambda(BaseModel):
    handler: NameHandlerTuple
    environment: Dict[str, str] = Field(default_factory=dict)

    @validator('handler', pre=True)
    def _split_handler(cls, v: Any) -> Tuple[str, str]:
        if not isinstance(v, str):
            raise TypeError('should be a str')
        if '.' not in v:
            raise ValueError('should have a module and function names')
        module, function = v.rsplit('.', maxsplit=1)
        return module, function


class ConfigEventSourceMapping(BaseModel):
    queue: str
    batch_size: int = 10
    maximum_batching_window: int = 0
    function_name: str


class Config(BaseModel):
    aws: ConfigAWS = Field(default_factory=ConfigAWS)
    secrets: Dict[str, Union[ConfigSecretString, ConfigSecretBinary]] = Field(default_factory=dict)
    topics: Dict[str, ConfigTopic] = Field(default_factory=dict)
    queues: Dict[str, ConfigQueue]
    lambdas: Dict[str, ConfigLambda]
    event_source_mapping: Dict[str, ConfigEventSourceMapping]

    @classmethod
    def from_toml(cls, fp: BinaryIO, /) -> 'Config':
        return cls.parse_obj(tomli.load(fp))
