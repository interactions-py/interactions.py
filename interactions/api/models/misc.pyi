from datetime import datetime
from typing import Optional, Union

# TODO: Reorganise these models based on which big obj uses little obj
# TODO: Potentially rename some model references to enums, if applicable
# TODO: Reorganise mixins to its own thing, currently placed here because circular import sucks.
# also, it should be serialiser* but idk, fl0w'd say something if I left it like that. /shrug

class DictSerializerMixin(object):
    __slots__ = "_json"

    _json: dict
    def __init__(self, **kwargs): ...

class Overwrite(DictSerializerMixin):
    __slots__ = ("_json", "id", "type", "allow", "deny")
    _json: dict
    id: int
    type: int
    allow: str
    deny: str
    def __init__(self, **kwargs): ...

class ClientStatus(DictSerializerMixin):
    __slots__ = ("_json", "desktop", "mobile", "web")
    _json: dict
    desktop: Optional[str]
    mobile: Optional[str]
    web: Optional[str]
    def __init__(self, **kwargs): ...

class Snowflake(object):
    _snowflake: str

    __slots__ = "_snowflake"
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

    __slots__ = (
        "USER",
        "USER_NICK",
        "CHANNEL",
        "ROLE",
        "EMOJI",
        "EMOJI_ANIMATED",
        "TIMESTAMP",
        "TIMESTAMP_SHORT_T",
        "TIMESTAMP_LONG_T",
        "TIMESTAMP_SHORT_D",
        "TIMESTAMP_LONG_D",
        "TIMESTAMP_SHORT_DT",
        "TIMESTAMP_LONG_DT",
        "TIMESTAMP_RELATIVE",
    )
    def stylize(self, format: str, **kwargs) -> str: ...
