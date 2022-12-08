from abc import ABC, abstractmethod
from typing import TypeVar

_T = TypeVar("_T")

__all__ = ("BaseAsyncContextManager", "BaseContextManager")


class BaseAsyncContextManager(ABC):
    """
    .. versionadded:: 4.3.2
    A base class for async context managers.
    """

    @abstractmethod
    def __init__(self):
        """Initialise the Context manager"""
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self):
        """Enter the context manager"""
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the context Manager"""
        raise NotImplementedError


class BaseContextManager(ABC):
    """
    .. versionadded:: 4.3.2

    A base class for context managers.
    """

    @abstractmethod
    def __init__(self):
        """Initialise the Context manager"""
        raise NotImplementedError

    @abstractmethod
    def __enter__(self):
        """Enter the context manager"""
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context Manager"""
        raise NotImplementedError
