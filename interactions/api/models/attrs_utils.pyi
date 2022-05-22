from typing import Any, TypeVar, Callable, Tuple, Union, Dict

import attrs
from attr import Attribute

from interactions.api.http.client import HTTPClient

_T = TypeVar("_T")

class MISSING:
    """A pseudosentinel based from an empty object. This does violate PEP, but, I don't care."""
    ...


@attrs.define(eq=False, init=False, on_setattr=attrs.setters.NO_OP)
class DictSerializerMixin:
    _json: dict = ...
    _extras: dict = ...
    """A dict containing values that were not serialized from Discord."""

    def __init__(self, kwargs_dict: dict = None, /, **other_kwargs): ...


@attrs.define(eq=False, init=False, on_setattr=attrs.setters.NO_OP)
class ClientSerializerMixin(DictSerializerMixin):
    _client: HTTPClient = ...
    def __init__(self, kwargs_dict: dict = None, /, **other_kwargs): ...


# This allows pyright to properly interpret the define() class decorator
def __dataclass_transform__(
    *,
    eq_default: bool = True,
    order_default: bool = False,
    kw_only_default: bool = False,
    field_descriptors: Tuple[Union[type, Callable[..., Any]], ...] = (()),
) -> Callable[[_T], _T]: ...


def field(**kwargs) -> Any: ...

define_defaults: Dict[str, Union[bool, object]] = ...
@__dataclass_transform__(eq_default=False, kw_only_default=True, field_descriptors=(field, attrs.field))
def define(**kwargs) -> Callable[[_T], _T]: ...

def convert_list(converter):
    """A helper function to convert items in a list with the specified converter"""

def convert_int(converter):
    """A helper function to pass an int to the converter, e.x. for Enums"""
