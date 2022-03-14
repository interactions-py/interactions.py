from collections import OrderedDict
from typing import Any, Dict, List, Optional, TypeVar

_T = TypeVar("_T")

class Storage:
    values: Any
    def __init__(self) -> None: ...
    def add(self, id: str, value: _T) -> OrderedDict: ...
    def get(self, id: str, default: Any = ...) -> Optional[Any]: ...
    def update(self, items: Dict[str, _T]) -> Dict[str, _T]: ...
    @property
    def view(self) -> List[dict]: ...

class Cache:
    dms: Any
    self_guilds: Any
    guilds: Any
    channels: Any
    roles: Any
    members: Any
    messages: Any
    users: Any
    interactions: Any
    def __init__(self) -> None: ...

ref_cache: Any
