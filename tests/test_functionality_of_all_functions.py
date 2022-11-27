# we want to run "every function" of the module once to ensure everything is fine and then test if every function works
# correctly in the other file.

# otherwise users could not implement a test for their function but still have a bug in them


from __future__ import annotations

import inspect
import types
import typing
from enum import Enum

import interactions

# from pprint import pprint


async def test_all_functions(fake_client):
    def get_function() -> typing.Generator[types.FunctionType | typing.Coroutine]:

        _exclude_classes: set = {
            "WebSocketClient",
            "Client",
            "DictSerializerMixin",
            "ClientSerializerMixin",
            "WSRateLimit",
            "MISSING",
            "_MISSING",
            "HTTPClient",
            "Route",
            "_Request",
        }
        _exclude_functions: set = {
            "extension_command",
            "extension_user_command",
            "extension_message_command",
            "extension_modal",
            "extension_component",
            "extension_listener",
            "extension_autocomplete",
            "get_logger",
            "option",
            "autodefer",
            "get",
        }

        _exclude: set = {*_exclude_functions, *_exclude_classes}

        for item in set(dir(interactions)):
            if (
                item.startswith("__")
                or inspect.ismodule(getattr(interactions, item))
                or item in _exclude
            ):
                continue
            klass: type
            if inspect.isclass(klass := getattr(interactions, item)):
                if issubclass(getattr(interactions, item), Enum):
                    continue
                members = inspect.getmembers(klass, predicate=inspect.isfunction)
                members = list(
                    filter(
                        lambda i: not i[0].startswith("_")
                        and "DictSerializerMixin.update" not in str(i[1]),
                        members,
                    )
                )

                if (
                    klass.__name__ == "Member"
                ):  # TODO remove this after testng and go on with edge cases
                    for member in members:
                        yield member[1]
            else:
                pass  # yield item

    for func in get_function():
        params = list(inspect.signature(func).parameters.values())
        for param in params:
            print(param, param.name)
