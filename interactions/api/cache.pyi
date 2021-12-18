from collections import OrderedDict
from typing import Any, List, Optional, Type

class Item(object):
    id: str
    value: Any
    type: Type
    def __init__(self, id: str, value: Any) -> None: ...

class Storage:
    values: OrderedDict
    def __init__(self) -> None: ...
    def add(self, item: Item) -> List[Item]: ...
    def get(self, id: str) -> Optional[Item]: ...
    @property
    def view(self) -> List[dict]: ...
    def update(self, item: Item) -> Optional[Item]: ...

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

ref_cache: Cache
