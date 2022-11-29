# we want to run "every function" of the module once to ensure everything is fine and then test if every function works
# correctly in the other file.

# otherwise users could not implement a test for their function but still have a bug in them


from __future__ import annotations

import inspect
import random
import string
import sys
import types
import typing
from datetime import datetime, timezone
from enum import Enum

if sys.version_info > (3, 8):
    from typing import ForwardRef, TypeVar, _BaseGenericAlias, get_args
else:
    from typing import ForwardRef, TypeVar, _GenericAlias as _BaseGenericAlias, get_args

import interactions

# from pprint import pprint

_T = TypeVar("_T", str, int, bool)


async def test_all_functions(fake_client, guild):
    def is_none(obj: type) -> bool:
        return obj is type(None) or obj is None  # noqa

    def is_built_in_class(obj: type):
        if str(obj) == "<method 'isoformat' of 'datetime.datetime' objects>":
            obj = str
        return obj.__module__ == "builtins" and not is_none(obj)

    def get_random_builtin_object_value(obj: type[_T]) -> _T:
        if obj == datetime.isoformat:
            return datetime.now(timezone.utc).isoformat()
        if obj == int:
            return random.randint(0, 100)
        elif obj == str:
            return "".join(random.choice(string.ascii_letters) for _ in range(10))

        elif obj == bool:
            return random.choice([True, False])

        else:
            raise TypeError(f"unexpected object {obj}!")

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
            # "create_auto_moderation_rule",
            "get_full_audit_logs",
            "get_latest_audit_log_action",
            "get_audit_logs",
            "modify_auto_moderation_rule",
            "modify_role_positions",
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
                        and "DictSerializerMixin.update" not in str(i[1])
                        and i[0] not in _exclude_functions,
                        members,
                    )
                )

                if klass.__name__ in {
                    "Member",
                    "Guild",
                    "User",
                    "Role",
                }:  # TODO remove this after testng and go on with edge cases
                    klass_inst = klass()  # todo eventually fix it (-> add required attribs)
                    if klass.__name__ == "Member":
                        klass_inst.user = interactions.User(id=random.randint(1, 9999))
                        klass_inst.roles = [987654321]
                        klass_inst._extras["guild_id"] = 987654321
                    if klass.__name__ == "Guild":
                        klass_inst = guild
                    klass_inst._client = fake_client._http
                    if not klass_inst.id:
                        klass_inst.id = 43988092
                    for member in members:
                        yield member[1], klass_inst
            else:
                pass  # yield item

    for func, klass_inst in get_function():
        kwargs: dict = {}

        kwargs["self"] = klass_inst
        if func.__qualname__ not in {"Member.get_guild_permissions", "Member.has_permissions"}:
            params = list(inspect.signature(func).parameters.values())
            for param in params:
                if param.name == "new_nick":
                    kwargs["new_nick"] = get_random_builtin_object_value(str)
                    continue

                if (
                    param.name == "self"
                    or param.default is not param.empty
                    and param.name != "guild_id"  # emtpy = required
                    and (
                        (
                            kwargs.get("entity_type") is not interactions.EntityType.EXTERNAL
                            and param.name != "channel_id"
                        )
                        or (
                            kwargs.get("entity_type") is interactions.EntityType.EXTERNAL
                            and param.name not in {"entity_metadata", "scheduled_end_time"}
                        )
                    )
                ):
                    continue
                elif param.name == "role_id":
                    kwargs["role_id"] = 125418155
                    continue

                elif isinstance(param.annotation, _BaseGenericAlias):
                    args = get_args(param.annotation)
                    if any(is_built_in_class(arg) for arg in args):
                        for arg in args:
                            if is_built_in_class(arg):
                                val = get_random_builtin_object_value(arg)
                                kwargs[param.name] = val
                                break
                    else:
                        for arg in args:
                            is_list = typing.List[arg] == param.annotation
                            if isinstance(arg, ForwardRef):
                                print(12345, func, param, arg)
                                raise NotImplementedError

                            arg: type
                            if is_none(arg):
                                continue

                            _kwargs = {}
                            if len(th := list(arg.__annotations__.values())) == 1:
                                if "Optional" in str(th):
                                    kwargs[param.name] = arg()
                                    continue
                                if isinstance(th[0], _BaseGenericAlias):
                                    typehints = get_args(th[0])
                                    if len(typehints) == 1:
                                        _type = typehints[0]
                                        if is_built_in_class(_type):
                                            val = get_random_builtin_object_value(_type)
                                        else:
                                            print(
                                                12345,
                                                func,
                                                param,
                                                arg,
                                            )
                                            raise NotImplementedError

                                        _kwargs[list(arg.__annotations__.keys())[0]] = val
                                    else:
                                        print(
                                            12345,
                                            func,
                                            param,
                                            arg,
                                        )
                                        raise NotImplementedError
                                else:
                                    print(
                                        12345,
                                        func,
                                        param,
                                        arg,
                                    )
                                    raise NotImplementedError

                            else:

                                for _ in range(random.randint(3, 100) if is_list else 1):

                                    for name, _type in arg.__annotations__.items():
                                        if "Optional" in str(_type):
                                            continue

                                        elif isinstance(_type, _BaseGenericAlias):
                                            print(
                                                12345,
                                                func,
                                                param,
                                                arg,
                                            )
                                            raise NotImplementedError

                                        elif is_built_in_class(_type):
                                            val = get_random_builtin_object_value(_type)

                                        elif issubclass(_type, Enum):
                                            choices = list(_type)
                                            if func.__name__ == "create_channel":
                                                choices.remove(10)
                                                choices.remove(11)
                                                choices.remove(12)
                                                choices.remove(1)
                                                choices.remove(3)
                                            val = random.choice(choices)

                                        _kwargs[name] = val
                                        if not kwargs.get(param.name):
                                            kwargs[param.name] = []
                                        kwargs[param.name].append(arg(**_kwargs))

                                if not kwargs.get(param.name):  # all args to class optional
                                    kwargs[param.name] = arg()

                            if not is_list:
                                kwargs[param.name] = arg(**_kwargs)

                else:
                    arg = param.annotation
                    if is_built_in_class(arg):
                        val = get_random_builtin_object_value(param.annotation)
                        kwargs[param.name] = val
                    else:
                        if issubclass(arg, Enum):
                            choices = list(arg)
                            if func.__name__ == "create_channel":
                                choices.remove(10)
                                choices.remove(11)
                                choices.remove(12)
                                choices.remove(1)
                                choices.remove(3)
                            val = random.choice(choices)
                            kwargs[param.name] = val
                        else:
                            if arg in {interactions.Image, interactions.File}:
                                val = random.randbytes(1000)
                                kwargs[param.name] = arg("random.png", val)
        res = func(**kwargs)
        if inspect.isawaitable(res):
            res = await res
