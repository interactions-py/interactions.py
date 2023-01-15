import logging
from typing import Any, TypeVar, Callable, Tuple, Union

import attrs
from attr import Attribute

# this took way too lonk to solve
# but this solution is based on https://www.attrs.org/en/stable/extending.html
# or, well, more specifically, the pyright section
# doing this in the actual file itself causes the function to return as a nonetype

_T = TypeVar("_T")

def __dataclass_transform__(
    *,
    eq_default: bool = True,
    order_default: bool = False,
    kw_only_default: bool = False,
    field_descriptors: Tuple[Union[type, Callable[..., Any]], ...] = (()),
) -> Callable[[_T], _T]: ...

log: logging.Logger

class_defaults: dict[str, bool | list[Callable]]
field_defaults: dict[str, bool]

def field(**kwargs) -> Any: ...
@__dataclass_transform__(eq_default=False, kw_only_default=True, field_descriptors=(field, attrs.field))
def define(**kwargs) -> Callable[[_T], _T]: ...
def docs(doc_string: str) -> dict[str, str]: ...
def str_validator(self, attribute: attrs.Attribute, value: Any) -> None: ...
def attrs_validator(
    validator: Callable, skip_fields: list[str] | None = None
) -> Callable[[Any, list[Attribute]], list[Attribute]]: ...
