import copy
from typing import Any, TypeVar, Coroutine, Callable

__all__ = ("CallbackObject",)

T = TypeVar("T", bound="CallbackObject")


class CallbackObject:
    _binding: Any
    callback: Callable[..., Coroutine[Any, Any, Any]]

    def __new__(cls, *args, **kwargs) -> T:
        self = super().__new__(cls)

        self._binding = None

        return self

    @property
    def has_binding(self) -> bool:
        return self._binding is not None

    def copy_with_binding(self, binding: Any = None) -> T:
        obj = copy.copy(self)
        obj._binding = binding
        return obj

    async def __call__(self, *args, **kwargs) -> Any:
        if self._binding:
            return await self.callback(self._binding, *args, **kwargs)
        return await self.callback(*args, **kwargs)

    async def call_with_binding(self, callback: Callable[..., Coroutine[Any, Any, Any]], *args, **kwargs) -> Any:
        """
        Call a given method using this objects _binding.

        Args:
            callback: The callback to call.
        """
        if self._binding:
            return await callback(self._binding, *args, **kwargs)
        return await callback(*args, **kwargs)
