import datetime
from io import FileIO, IOBase
from logging import Logger
from typing import Optional, Union, List
from enum import IntEnum

from interactions.api.models.attrs_utils import DictSerializerMixin, define

log: Logger

@define()
class AutoModMetaData(DictSerializerMixin):
    channel_id: Optional[Snowflake]
    duration_seconds: Optional[int]

class AutoModTriggerType(IntEnum):
    KEYWORD: int
    HARMFUL_LINK: int
    SPAM: int
    KEYWORD_PRESET: int

class AutoModKeywordPresetTypes(IntEnum):
    PROFANITY: int
    SEXUAL_CONTENT: int
    SLURS: int

@define()
class AutoModAction(DictSerializerMixin):
    type: int
    metadata: Optional[AutoModMetaData]

@define()
class AutoModTriggerMetadata(DictSerializerMixin):
    keyword_filter: Optional[List[str]]
    presets: Optional[List[str]]

@define()
class Overwrite(DictSerializerMixin):
    id: int
    type: int
    allow: str
    deny: str

@define()
class ClientStatus(DictSerializerMixin):
    desktop: Optional[str]
    mobile: Optional[str]
    web: Optional[str]

class Snowflake:
    _snowflake: str
    def __init__(self, snowflake: Union[int, str, "Snowflake"]) -> None: ...
    def __int__(self): ...
    @property
    def increment(self) -> int: ...
    @property
    def worker_id(self) -> int: ...
    @property
    def process_id(self) -> int: ...
    @property
    def epoch(self) -> float: ...
    @property
    def timestamp(self) -> datetime.datetime: ...
    def __hash__(self): ...
    def __eq__(self, other): ...

class Color:
    @property
    def blurple(self) -> hex: ...
    @property
    def green(self) -> hex: ...
    @property
    def yellow(self) -> hex: ...
    @property
    def fuchsia(self) -> hex: ...
    @property
    def red(self) -> hex: ...
    @property
    def white(self) -> hex: ...
    @property
    def black(self) -> hex: ...

class File:
    def __init__(
        self, filename: str, fp: Optional[IOBase] = ..., description: Optional[str] = ...
    ) -> None: ...

class Image:
    _URI: str
    _name: str

    def __init__(self, file: Union[str, FileIO], fp: Optional[IOBase] = ...) -> None: ...
    @property
    def data(self) -> str: ...
    @property
    def filename(self) -> str: ...
