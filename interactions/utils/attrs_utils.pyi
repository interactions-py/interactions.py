from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union, overload

import attrs

from interactions.api.http.client import HTTPClient

_T = TypeVar("_T")
_P = TypeVar("_P")


@attrs.define(eq=False, init=False, on_setattr=attrs.setters.NO_OP)
class DictSerializerMixin:
    _json: dict = attrs.field(init=False)
    _extras: dict = attrs.field(init=False)
    """A dict containing values that were not serialized from Discord."""
    __deepcopy_kwargs__: bool = attrs.field(init=False)
    """Should the kwargs be deepcopied or not?"""

    def __init__(self, kwargs_dict: dict = None, /, **other_kwargs): ...


@attrs.define(eq=False, init=False, on_setattr=attrs.setters.NO_OP)
class ClientSerializerMixin(DictSerializerMixin):
    _client: HTTPClient = attrs.field(init=False)
    def __init__(self, kwargs_dict: dict = None, /, **other_kwargs): ...

# This allows pyright to properly interpret the define() class decorator
def __dataclass_transform__(
    *,
    eq_default: bool = True,
    order_default: bool = False,
    kw_only_default: bool = False,
    field_descriptors: Tuple[Union[type, Callable[..., Any]], ...] = (()),
) -> Callable[[_T], _T]: ...
@wraps(attrs.field())
def field(
    converter=None,
    default=attrs.NOTHING,
    repr=False,
    add_client: bool = False,
    discord_name: str = None,
    **kwargs,
) -> Any: ...

define_defaults: Dict[str, Union[bool, object]] = ...

@__dataclass_transform__(
    eq_default=False, kw_only_default=True, field_descriptors=(field, attrs.field)
)
def define(**kwargs) -> Callable[[_T], _T]: ...
def convert_list(converter: Callable[[_T], _P]) -> Callable[[List[_T]], List[_P]]:
    """A helper function to convert items in a list with the specified converter"""

def convert_int(converter: Callable[[int], _T]) -> Callable[[Any], _T]:
    """A helper function to pass an int to the converter, e.x. for Enums"""

def convert_type(type_: Type[_T], *, classmethod: Optional[str] = None) -> Callable[[Any], _T]:
    """A helper function to convert an input to a specified type."""

def convert_dict(
    key_converter: Optional[Callable[[Any], _T]] = None,
    value_converter: Optional[Callable[[Any], _P]] = None,
) -> Callable[[Dict[Any, Any]], Dict[_T, _P]]:
    """A helper function to convert the keys and values of a dictionary with the specified converters"""

@overload
def deepcopy_kwargs() -> Callable[[_T], _T]: ...
@overload
def deepcopy_kwargs(cls: _T) -> _T: ...
def deepcopy_kwargs(cls: Optional[_T] = None) -> Union[Callable[[_T], _T], _T]:
    """
    A decorator to make the DictSerializerMixin deepcopy the kwargs before processing them.
    This can help avoid weird bugs with some objects, though will error out in others.
    """
