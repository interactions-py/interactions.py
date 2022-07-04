from asyncio import sleep
from inspect import isfunction
from logging import getLogger
from typing import Coroutine, Iterable, List, Type, TypeVar, Union, _GenericAlias, get_args

from ..api.error import LibraryException
from ..api.http.client import HTTPClient
from ..api.models.channel import Channel
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
            message="`force_cache` and `force_http` are mutually exclusive", code=12
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
        if isinstance(obj, _GenericAlias):
            _obj = get_args(obj)[0]
            _objects: List[_obj] = []

            # TODO: add cache, include getting for IDs that are `None`

            if len(list(kwargs)) == 2:
                if guild_id := kwargs.pop("guild_id", None):
                    _guild = Guild(**await client._http.get_guild(guild_id), _client=client._http)
                    _func = getattr(_guild, _name)

                elif channel_id := kwargs.pop("channel_id", None):
                    _channel = Channel(
                        **await client._http.get_channel(channel_id), _client=client._http
                    )
                    _func = getattr(_channel, _name)

            else:
                _func = getattr(client._http, _name)

            _kwarg_name = list(kwargs)[0][:-1]

            for kwarg in kwargs.get(list(kwargs)[0]):
                _kwargs = {_kwarg_name: kwarg}
                __obj = await _func(**_kwargs)

                if isinstance(__obj, dict):
                    _objects.append(_obj(**__obj, _client=client._http))
                else:
                    _objects.append(__obj)

            return _objects

        _obj: _T = None

        if not (force_http := kwargs.get("force_http", False)):
            if isinstance(obj, Member):
                _values = (
                    kwargs.get("guild_id"),
                    kwargs.get("member_id"),
                )  # Fuck it, I can't be dynamic on this
            else:
                if len(kwargs) == 2:
                    kwargs.pop("channel_id", None)
                    kwargs.pop("guild__id", None)
                _values = Snowflake(kwargs.get(list(kwargs)[0]))

            _obj = client.cache[obj].get(_values)

        if kwargs.get("force_cache", False):
            return _obj

        elif not force_http and obj:
            return __cache(obj)

        else:
            if obj in (Role, Emoji):
                _guild = Guild(
                    **await client._http.get_guild(kwargs.pop("guild_id")), _client=client._http
                )
                _func = getattr(_guild, _name)
                return await _func(**kwargs)

            _func = getattr(client._http, _name)
            return __http_request(obj, _func(**kwargs), client._http)

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
    obj: Union[Type[_T], List[Type[_T]]], request: Coroutine, http: HTTPClient
) -> Union[_T, List[_T]]:
    if not isinstance(obj, list):
        _obj = await request
        return obj(**_obj, _client=http)


async def __cache(obj: _T) -> _T:
    await sleep(0.00001)  # iirc Bluenix meant that any coroutine should await at least once
    return obj
