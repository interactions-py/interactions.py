from enum import IntEnum
from string import Formatter
from typing import Any, Dict, Optional, Union

class ErrorFormatter(Formatter):
    def get_value(self, key, args, kwargs) -> Any: ...

class InteractionException(Exception):
    __slots__ = ("_type", "_lookup", "__type", "_formatter", "kwargs")
    _type: Union[int, IntEnum]
    __type: Optional[Union[int, IntEnum]]
    _formatter: ErrorFormatter
    kwargs: Dict[str, Any]
    _lookup: dict
    def __init__(self, __type: Optional[Union[int, IntEnum]] = 0, **kwargs) -> None: ...
    @staticmethod
    def lookup() -> dict: ...
    @property
    def type(self) -> Optional[Union[int, IntEnum]]: ...
    def error(self) -> None: ...

class GatewayException(InteractionException):
    __slots__ = ("_type", "_lookup", "__type", "_formatter", "kwargs")
    _type: Union[int, IntEnum]
    __type: Optional[Union[int, IntEnum]]
    _formatter: ErrorFormatter
    kwargs: Dict[str, Any]
    _lookup: dict
    def __init__(self, __type, **kwargs): ...
    @staticmethod
    def lookup() -> dict: ...

class HTTPException(InteractionException):
    __slots__ = ["_type", "_lookup", "__type", "_formatter", "kwargs"]
    _type: Union[int, IntEnum]
    __type: Optional[Union[int, IntEnum]]
    _formatter: ErrorFormatter
    kwargs: Dict[str, Any]
    _lookup: dict
    def __init__(self, __type, **kwargs): ...
    @staticmethod
    def lookup() -> dict: ...

class JSONException(InteractionException):
    __slots__ = ["_type", "_lookup", "__type", "_formatter", "kwargs"]
    _type: Union[int, IntEnum]
    __type: Optional[Union[int, IntEnum]]
    _formatter: ErrorFormatter
    kwargs: Dict[str, Any]
    _lookup: dict
    def __init__(self, __type, **kwargs): ...
    @staticmethod
    def lookup() -> dict: ...
