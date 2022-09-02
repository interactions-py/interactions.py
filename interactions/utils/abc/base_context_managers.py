from abc import ABCMeta, abstractmethod
from typing import TypeVar

_T = TypeVar("_T")

__all__ = ("BaseAsyncContextManager", "BaseContextManager")


class BaseAsyncContextManager(metaclass=ABCMeta):
    """A base class for async iterators."""

    # I don't want to make it subclass the BaseContextManager since it forces implementation of __enter__ and __exit__

    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self):
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError


class BaseContextManager(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    @abstractmethod
    def __enter__(self):
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError
