from typing import ClassVar

class _Missing:
    """A sentinel object for places where None is a valid value"""
    _instance: ClassVar["_Missing"] = None

    def __eq__(self, other): ...

    def __repr__(self): ...

    def __hash__(self): ...

    def __bool__(self): ...


MISSING = _Missing()
