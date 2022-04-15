import logging
from datetime import datetime
from typing import Optional, Union
from io import IOBase, FileIO

log: logging.Logger

class DictSerializerMixin(object):
    _json: dict
    def __init__(self, **kwargs): ...

class Overwrite(DictSerializerMixin):
    _json: dict
    id: int
    type: int
    allow: str
    deny: str
    def __init__(self, **kwargs): ...

class ClientStatus(DictSerializerMixin):
    _json: dict
    desktop: Optional[str]
    mobile: Optional[str]
    web: Optional[str]
    def __init__(self, **kwargs): ...

class Snowflake(object):
    _snowflake: str
    def __init__(self, snowflake: Union[int, str, "Snowflake"]) -> None: ...
    @property
    def increment(self) -> int: ...
    @property
    def worker_id(self) -> int: ...
    @property
    def process_id(self) -> int: ...
    @property
    def epoch(self) -> float: ...
    @property
    def timestamp(self) -> datetime: ...
    # By inheritance logic, __str__ and __hash__ are already defined in headers.
    # Just because we can :)
    def __hash__(self) -> int: ...
    def __str__(self) -> str: ...
    def __int__(self) -> int: ...
    def __eq__(self, other) -> Union[bool, NotImplemented]: ...

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

class Format:
    USER: str
    USER_NICK: str
    CHANNEL: str
    ROLE: str
    EMOJI: str
    EMOJI_ANIMATED: str
    TIMESTAMP: str
    TIMESTAMP_SHORT_T: str
    TIMESTAMP_LONG_T: str
    TIMESTAMP_SHORT_D: str
    TIMESTAMP_LONG_D: str
    TIMESTAMP_SHORT_DT: str
    TIMESTAMP_LONG_DT: str
    TIMESTAMP_RELATIVE: str
    def stylize(self, format: str, **kwargs) -> str: ...

class MISSING: ...

class File(object):
    _filename: str
    _fp: IOBase
    _description: str
    def __init__(
        self,
        filename: str,
        fp: Optional[IOBase] = MISSING,
        description: Optional[str] = MISSING
    ) -> None: ...
    def _json_payload(self, id) -> dict: ...

class Image(object):

    _URI: str
    _name: str

    def __init__(self, file: Union[str, FileIO], fp: Optional[IOBase] = MISSING): ...
    @property
    def data(self) -> str: ...
    @property
    def filename(self) -> str: ...
