import logging
from datetime import datetime
from typing import Optional, Union

# TODO: Potentially rename some model references to enums, if applicable
# TODO: Reorganise mixins to its own thing, currently placed here because circular import sucks.
# also, it should be serialiser* but idk, fl0w'd say something if I left it like that. /shrug

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

class Format(object):
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
