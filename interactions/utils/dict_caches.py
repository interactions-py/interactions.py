from collections import OrderedDict
from typing import Generic, TypeVar

from .missing import MISSING

__all__ = ("FIFODict", "LRUDict")

_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


class FIFODict(OrderedDict, Generic[_KT, _VT]):
    """
    .. versionadded:: 4.4.0

    A dictionary that removes the old keys if over the item limit
    """

    def __init__(self, *args, max_items: int = float("inf"), **kwargs):
        if max_items < 0:
            raise RuntimeError("You cannot set max_items to negative numbers.")

        super().__init__(*args, **kwargs)
        self._max_items = max_items

    def __setitem__(self, key: _KT, value: _VT):
        super().__setitem__(key, value)

        # Prevent buildup over time
        while len(self) > self._max_items:
            del self[next(iter(self))]


class LRUDict(OrderedDict, Generic[_KT, _VT]):
    """
    .. versionadded:: 4.4.0

    A dictionary that removes the value that was the least recently used if over the item limit
    """

    def __init__(self, *args, max_items: int = float("inf"), **kwargs):
        if max_items < 0:
            raise RuntimeError("You cannot set max_items to negative numbers.")

        super().__init__(*args, **kwargs)
        self._max_items = max_items

    def __getitem__(self, key: _KT) -> _VT:
        self.move_to_end(key)
        return super().__getitem__(key)

    def __setitem__(self, key: _KT, value: _VT):
        super().__setitem__(key, value)

        # Prevent buildup over time
        while len(self) > self._max_items:
            del self[next(iter(self))]

    __marker = object()

    def pop(self, key: _KT, default: _VT = __marker) -> _VT:
        if key in self:
            result = self[key]
            del self[key]
            return result
        if default is MISSING:
            raise KeyError(key)
        return default
