from typing import ClassVar

__all__ = ("MISSING",)


class _Missing:
    """
    .. versionadded:: 4.1.0
        Added MISSING as pseudo-sentinel

    .. versionchanged:: 4.3.2
        Turned MISSING into a proper sentinel

    A sentinel object for places where None is a valid value
    """

    _instance: ClassVar["_Missing"] = None

    def __new__(cls):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance

    def __eq__(self, other):
        return self.__class__ is other.__class__

    def __repr__(self):
        return "<interactions.MISSING>"

    def __hash__(self):
        return 0

    def __bool__(self):
        return False


MISSING = _Missing()
