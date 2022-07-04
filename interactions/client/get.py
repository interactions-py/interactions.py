from asyncio import sleep
from inspect import isawaitable, isfunction
from logging import getLogger
from typing import Coroutine, Iterable, List, Type, TypeVar, Union, _GenericAlias, get_args

from ..api.error import LibraryException
from ..api.http.client import HTTPClient
from ..api.models.guild import Guild
from ..api.models.member import Member
from ..api.models.message import Emoji
from ..api.models.misc import Snowflake
from ..api.models.role import Role
from .bot import Client

log = getLogger("get")

_T = TypeVar("_T")

__all__ = ("get",)


def get(*args, **kwargs):
    # sourcery no-metrics

    if len(args) == 2 and any(isinstance(_, Iterable) for _ in args):
        raise LibraryException(message="You can only use Iterables as single-argument!", code=12)

    if kwargs.get("force_http", None) and kwargs.get("force_cache", None):
        raise LibraryException(
            message="`force_cache` and `force_http` are mutually exclusive!", code=12
        )

    if len(args) == 2:
        client: Client
        obj: Union[Type[_T], Type[List[_T]]]

        client, obj = args
        if not isinstance(obj, type) and not isinstance(obj, _GenericAlias):
            raise LibraryException(
                message="The object must not be an instance of a class!", code=12
            )

        _name = f"get_{obj.__name__.lower()}"
        __name = f"{obj.__name__.lower()}_id"
        if isinstance(obj, _GenericAlias):
            _obj = get_args(obj)[0]
            _objects: List[_obj] = []

            force_cache = kwargs.pop("force_cache", False)

            if not (force_http := kwargs.pop("force_http", False)):
                __name += "s"
                if isinstance(_obj, Member):  # Can't be more dynamic on this
                    _values = ()
                    _guild_id = Snowflake(kwargs.get("guild_id"))
                    for _id in kwargs.get("member_ids"):
                        _values += (
                            (
                                _guild_id,
                                Snowflake(_id),
                            ),
                        )
                    for item in _values:
                        _objects.append(client.cache[obj].get(item))

                else:
                    kwargs.get("channel_id", None)
                    kwargs.get("guild_id", None)
                    for _id in kwargs.get(__name):
                        _objects.append(client.cache[obj].get(Snowflake(_id), None))

            if force_cache:
                return _objects

            elif not force_http and None not in _objects:
                return __cache(_objects)

            elif force_http:
                _objects.clear()
                _func = getattr(_name, client._http)
                for _id in kwargs.get(__name):
                    _kwargs = kwargs
                    _kwargs.pop(__name)
                    _kwargs[__name[:-1]] = _id
                    _objects.append(_func(**_kwargs)

                return __http_request(_obj, request=_objects, http=client.http)

            else:
                _func = getattr(_name, client._http)
                for _index, __obj in enumerate(_objects):
                    if __obj is None:
                        _id = kwargs.get(__name)[_index]
                        _kwargs = kwargs
                        _kwargs.pop(__name)
                        _kwargs[__name[:-1]] = _id
                        _request = _func(**_kwargs)
                        _objects[_index] = _request

                return __http_request(_obj, request=_objects, http=client._http)

        _obj: _T = None

        force_cache = kwargs.pop("force_cache", False)

        if not (force_http := kwargs.pop("force_http", False)):
            if isinstance(obj, Member):
                _values = (
                    Snowflake(kwargs.get("guild_id")),
                    Snowflake(kwargs.get("member_id")),
                )  # Fuck it, I can't be dynamic on this
            else:
                if len(kwargs) == 2:
                    kwargs.get("channel_id", None)
                    kwargs.get("guild_id", None)
                _values = Snowflake(kwargs.get(__name))

            _obj = client.cache[obj].get(_values)

        if force_cache:
            return _obj

        elif not force_http and _obj:
            return __cache(_obj)

        else:
            return __http_request(obj=obj, request=None, http=client._http, _name=_name, **kwargs)

    elif len(args) == 1:

        def run_check(_obj, _check):
            return _check(_obj)

        item: Iterable = args[0]
        if not isinstance(item, Iterable):
            raise LibraryException(message="The specified item must be an iterable!", code=12)

        if not kwargs:
            raise LibraryException(
                message="You have to specify either the name, id or a custom check to check against!",
                code=12,
            )

        if len(list(kwargs)) > 1:
            raise LibraryException(
                message="Only one keyword argument to check against is allowed!", code=12
            )

        _arg = str(list(kwargs)[0])

        __obj = next(
            (
                _
                for _ in item
                if (
                    str(getattr(_, _arg, None)) == str(kwargs.get(_arg))
                    if not isfunction(kwargs.get(_arg))
                    else run_check(item, kwargs.get(_arg))
                )
            ),
            None,
        )
        return __obj


async def __http_request(
    obj: Type[_T]],
    http: HTTPClient,
    request: Union[Coroutine, List[_T, Coroutine]] = None,
    _name=None,
    **kwargs,
) -> Union[_T, List[_T]]:

    if not request:
        if obj in (Role, Emoji):
            _guild = Guild(**await http.get_guild(kwargs.pop("guild_id")), _client=http)
            _func = getattr(_guild, _name)
            return await _func(**kwargs)

        _func = getattr(http, _name)
        _obj = await _func
        return obj(**_obj, _client=http)

    if not isinstance(request, list):
        return obj(**await request, _client=http)

    return [obj(**await req, _client=http) if isawaitable(req) else req for req in request]

async def __cache(obj: _T) -> _T:
    await sleep(0.00001)  # iirc Bluenix meant that any coroutine should await at least once
    return obj
