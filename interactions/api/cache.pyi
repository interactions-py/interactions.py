import asyncio
from collections import OrderedDict
from typing import Any, Dict, List, Optional, TypeVar, Union, Tuple

_T = TypeVar("_T")
key = Union[str, Tuple[str, str]]

class Storage:
    values: OrderedDict
    ttl: Optional[float]
    _timeouts: Dict[str, asyncio.Task]
    def __init__(self, ttl: Optional[float] = ...) -> None: ...
    async def _clear_item(self, id: key) -> None: ...
    def add(self, id: key, value: Any) -> OrderedDict: ...
    def get(self, id: key, default: Any = ...) -> Optional[Any]: ...
    def update(self, items: Dict[key, _T]) -> Dict[key, _T]: ...
    @property
    def view(self) -> List[dict]: ...

class Cache:
    dms: Storage
    guilds: Storage
    channels: Storage
    roles: Storage
    members: Storage
    messages: Storage
    users: Storage
    interactions: Storage
    def __init__(self) -> None: ...

ref_cache: Cache
