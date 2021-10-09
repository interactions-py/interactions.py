from collections import OrderedDict
from typing import Any, Dict, List, Optional, Type

class Item(object):
    __slots__ = ("id", "value", "type")
    id: str
    value: Any
    type: Type
    def __init__(self, id: str, value: Any) -> None: ...

class Storage:
    __slots__ = "values"
    values: OrderedDict
    def __init__(self) -> None: ...
    def add(self, item: Item) -> List[Item]: ...
    def get(self, id: str) -> Optional[Item]: ...

class Cache:
    token: str
    dms: Storage
    self_guilds: Storage
    guilds: Storage
    channels: Storage
    roles: Storage
    members: Storage
    messages: Storage
    users: Storage
    interactions: Storage
    def __init__(self) -> None: ...
