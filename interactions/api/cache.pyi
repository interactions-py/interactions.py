from collections import OrderedDict
from typing import Any, List, Optional, TypeVar, Type, Union

_T = TypeVar("_T")

class Item(object):
    id: str
    value: Any
    type: type
    def __init__(self, id: str, value: Any) -> None: ...

class Cache:
    values: OrderedDict[str, Item]
    def __init__(self) -> None: ...
    def add(self, item: Item) -> List[Item]: ...
    def get(self, id: str, default: _T = None) -> Union[Item, _T]: ...
    def update(self, item: Item) -> Optional[Item]: ...
    def get_types(self, type: Type[_T]) -> List[_T]: ...

ref_cache: Cache
