from functools import wraps
from typing import Tuple

import attrs


class MISSING:
    """A pseudosentinel based from an empty object. This does violate PEP, but, I don't care."""

    ...


@attrs.define(eq=False, init=False, on_setattr=attrs.setters.NO_OP)
class DictSerializerMixin:
    _json: dict = attrs.field(init=False, repr=False)
    _extras: dict = attrs.field(init=False, repr=False)
    """A dict containing values that were not serialized from Discord."""

    def __init__(self, kwargs_dict: dict = None, /, **other_kwargs):
        kwargs = kwargs_dict or other_kwargs
        client = kwargs.pop("_client", None)
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
                    if value is not None and attrib.metadata.get("add_client"):
                        if isinstance(value, list):
                            for item in value:
                                item["_client"] = client
                        else:
                            value["_client"] = client

                    passed_kwargs[attrib_name] = value

        self._extras = kwargs
        self.__attrs_init__(**passed_kwargs)  # type: ignore


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
        return [converter(**item) for item in list] if list is not None else None

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


define_defaults = dict(
    repr=False, kw_only=True, eq=False, init=False, on_setattr=attrs.setters.NO_OP
)


@wraps(attrs.define)
def define(**kwargs):
    return attrs.define(**kwargs, **define_defaults)


@wraps(attrs.field)
def field(
    converter=None,
    default=attrs.NOTHING,
    add_client: bool = False,
    discord_name: str = None,
    **kwargs,
):
    if converter is not None and default is None:
        converter = attrs.converters.optional(converter)

    metadata = kwargs.get("metadata", {})
    if add_client:
        metadata["add_client"] = True
    if discord_name is not None:
        metadata["discord_name"] = discord_name

    return attrs.field(converter=converter, default=default, metadata=metadata, **kwargs)
