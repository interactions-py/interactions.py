from copy import deepcopy
from functools import wraps
from typing import Dict, Mapping, Optional, Tuple

import attrs

from .missing import MISSING

__all__ = (
    "DictSerializerMixin",
    "ClientSerializerMixin",
)


@attrs.define(eq=False, init=False, on_setattr=attrs.setters.NO_OP)
class DictSerializerMixin:
    _json: dict = attrs.field(init=False, repr=False)
    _extras: dict = attrs.field(init=False, repr=False)
    """A dict containing values that were not serialized from Discord."""

    __deepcopy_kwargs__ = False
    """Should the kwargs be deepcopied or not?"""

    def __init__(self, kwargs_dict: dict = None, /, **other_kwargs):
        # sourcery skip: low-code-quality
        kwargs = kwargs_dict or other_kwargs
        client = kwargs.pop("_client", None)

        if self.__deepcopy_kwargs__:
            kwargs = deepcopy(kwargs)

        self._json = kwargs.copy()
        passed_kwargs = {}

        attribs: Tuple[attrs.Attribute, ...] = self.__attrs_attrs__  # type: ignore
        for attrib in attribs:
            if attrib.init:
                # attrs is weird
                attrib_name = attrib.name
                if attrib_name[0] == "_":
                    attrib_name = attrib_name[1:]

                if discord_name := attrib.metadata.get("discord_name"):
                    discord_name = discord_name
                else:
                    discord_name = attrib_name

                if (value := kwargs.pop(discord_name, MISSING)) is not MISSING:
                    if (
                        value is not None
                        and attrib.metadata.get("add_client")
                        and client is not None
                    ):
                        if isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict):
                                    item["_client"] = client
                                elif isinstance(item, DictSerializerMixin):
                                    item._client = client
                        else:
                            if isinstance(value, dict):
                                value["_client"] = client
                            elif isinstance(value, DictSerializerMixin):
                                value._client = client

                    # make sure json is recursively handled
                    if isinstance(value, list):
                        self._json[attrib_name] = [
                            i._json if isinstance(i, DictSerializerMixin) else i for i in value
                        ]
                    elif isinstance(value, DictSerializerMixin):
                        self._json[attrib_name] = value._json  # type: ignore

                    passed_kwargs[attrib_name] = value

                elif attrib.default is not attrs.NOTHING:
                    # handle defaults like attrs does
                    default = attrib.default
                    if isinstance(default, attrs.Factory):  # type: ignore
                        passed_kwargs[attrib_name] = (
                            default.factory(self) if default.takes_self else default.factory()
                        )
                    else:
                        passed_kwargs[attrib_name] = default
                else:
                    passed_kwargs[attrib_name] = None

        self._extras = kwargs
        self.__attrs_init__(**passed_kwargs)  # type: ignore

    def update(self, kwargs_dict: dict = None, /, **other_kwargs):
        """
        Update an object with new attributes.
        All data will be converted, and any extra attributes will be put in _extras

        :param dict kwargs_dict: The dictionary to update from
        """
        # idiot check to make sure it's a dictionary (yes, that includes myself)
        if isinstance(kwargs_dict, DictSerializerMixin):
            kwargs_dict = kwargs_dict._json

        kwargs = kwargs_dict or other_kwargs
        attribs: Dict[str, attrs.Attribute] = {
            attrib.name: attrib for attrib in self.__attrs_attrs__
        }

        for name, value in kwargs.items():
            if name not in attribs:
                self._extras[name] = value
                continue

            if value is None:
                continue

            self._json[name] = value
            setattr(
                self, name, converter(value) if (converter := attribs[name].converter) else value
            )


@attrs.define(eq=False, init=False, on_setattr=attrs.setters.NO_OP)
class ClientSerializerMixin(DictSerializerMixin):
    _client = attrs.field(init=False, repr=False)

    def __init__(self, kwargs_dict: dict = None, /, **other_kwargs):
        kwargs = kwargs_dict or other_kwargs
        self._client = kwargs.get("_client", None)
        super().__init__(**kwargs)


def convert_list(converter):
    """A helper function to convert items in a list with the specified converter"""

    def inner_convert_list(list):
        if list in (MISSING, None):
            return list

        # empty lists need no conversion
        if len(list) == 0:
            return list

        # all items should be of the same type
        if isinstance(list[0], Mapping):
            return [converter(**item) for item in list]

        # check if all are from the mixin and have been converted
        elif issubclass(converter, DictSerializerMixin) and isinstance(
            list[0], DictSerializerMixin
        ):
            return list

        else:
            return [converter(item) for item in list]

    return inner_convert_list


def convert_int(converter):
    """A helper function to pass an int to the converter, e.x. for Enums"""

    def inner_convert_int(num):
        return converter(int(num)) if num is not None else None

    return inner_convert_int


def convert_dict(key_converter=None, value_converter=None):
    """A helper function to convert the keys and values of a dictionary with the specified converters"""

    def _return_same(value):
        return value

    if key_converter is None:
        key_converter = _return_same
    if value_converter is None:
        value_converter = _return_same

    def inner_convert_dict(dict):
        return {key_converter(key): value_converter(value) for key, value in dict.items()}

    return inner_convert_dict


def convert_type(type_: type, *, classmethod: Optional[str] = None):
    """A helper function to convert an input to a specified type."""

    def inner_convert_object(value):
        if not classmethod:
            return value if isinstance(value, type_) else type_(value)
        else:
            return value if isinstance(value, type_) else getattr(type_, classmethod)(value)

    return inner_convert_object


def deepcopy_kwargs(cls: Optional[type] = None):
    """
    A decorator to make the DictSerializerMixin deepcopy the kwargs before processing them.
    This can help avoid weird bugs with some objects, though will error out in others.
    """

    def decorator(cls: type):
        cls.__deepcopy_kwargs__ = True  # type: ignore
        return cls

    if cls is not None:
        cls.__deepcopy_kwargs__ = True  # type: ignore
        return cls

    return decorator


define_defaults = dict(kw_only=True, eq=False, init=False, on_setattr=attrs.setters.NO_OP)


@wraps(attrs.define)
def define(**kwargs):
    return attrs.define(**kwargs, **define_defaults)


@wraps(attrs.field)
def field(
    converter=None,
    default=attrs.NOTHING,
    repr=True,
    add_client: bool = False,
    discord_name: str = None,
    **kwargs,
):
    if converter is not None:
        if isinstance(converter, type):
            converter = convert_type(converter)
        converter = attrs.converters.optional(converter)

    metadata = kwargs.get("metadata", {})
    if add_client:
        metadata["add_client"] = True
    if discord_name is not None:
        metadata["discord_name"] = discord_name

    return attrs.field(converter=converter, default=default, repr=repr, metadata=metadata, **kwargs)
