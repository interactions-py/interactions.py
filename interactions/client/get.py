from asyncio import sleep
from enum import Enum
from inspect import isawaitable, isfunction
from logging import getLogger
from typing import Coroutine, Iterable, List, Type, TypeVar, Union, get_args

try:
    from typing import _GenericAlias

except ImportError:
    from typing import _BaseGenericAlias as _GenericAlias

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

__all__ = (
    "get",
    "Force",
)


class Force(str, Enum):
    """
    An enum representing the force methods for the get method

    :ivar str CACHE: Enforce the usage of cache and block the usage of http
    :ivar str HTTP: Enforce the usage of http and block the usage of cache
    """

    CACHE = "cache"
    HTTP = "http"


def get(*args, **kwargs):
    """
    Helper method to get an object.

    This method can do the following:
        * Get a list of a specific objects
            * purely from cache
            * purely from HTTP
            * from cache and additionally from HTTP for every ID that was not found in cache
        * Get a single specific object
            * purely from cache
            * purely from HTTP
            * from HTTP if not found in cache else from cache
        * Get an object from an iterable
            * based of its name
            * based of its ID
            * based of a custom check

    The method has to be awaited when:
        * You don't force anything
        * You force HTTP
    The method has not to be awaited when:
        * You get from an iterable
        * You force cache

    .. note ::
        Technically, there is no need for an ``await`` if there is an object found in the cache. Because of the fact,
        that, as long as you don't enforce the cache, the function will get the object from HTTP, if it is not in the
        cache, you still have to await it. This has been done to reduce confusion on whether the object origins from
        an HTTP call or a cache result and to remove the extra step for you to check if the returned object is an
        awaitable or not.


    Forcing:
        Forcing can be done via the ``force`` keyword argument.
            * ``force="cache"`` or ``force=interactions.Force.CACHE``:
                This forces the method to only return from cache (if the object is not found it will return ``None``). If
                you use this, you don't need to await the method.

            * ``force="http"`` or ``force=interactions.Force.HTTP``:
                This forces the method to make an HTTP request to the discord API and return the result of it. If you
                use this, you have to await the method.

                .. attention ::
                    If you are a PyCharm user, please be aware of a bug that causes incorrect suggestions to appear if
                    using an enum. Even if PyCharm shows a normal object as result, you have to await the method if you
                    enforce HTTP. To prevent this bug from happening it is suggested using ``force="http"`` instead of
                    the enum.

    """

    def get_cache(_object: Type[_T], _list: bool = False) -> Union[_T, List[_T]]:
        nonlocal kwarg_name

        if _list:
            _obj = []
            if isinstance(_object, Member):  # Can't be more dynamic on this
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
                    _objects.append(client.cache[_object].get(item))

            else:
                _obj.extend(
                    client.cache[_object].get(Snowflake(_id), None)
                    for _id in kwargs.get(kwarg_name)
                )
        else:
            if isinstance(_object, Member):
                _values = (
                    Snowflake(kwargs.get("guild_id")),
                    Snowflake(kwargs.get("member_id")),
                )  # Fuck it, I can't be dynamic on this
            else:
                _values = Snowflake(kwargs.get(kwarg_name))

            _obj = client.cache[_object].get(_values)
        return _obj

    def search_iterable(*args, **kwargs):

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
                    else kwargs.get(_arg)(item)
                )
            ),
            None,
        )
        return __obj

    if len(args) == 2 and any(isinstance(_, Iterable) for _ in args):
        raise LibraryException(message="You can only use Iterables as single-argument!", code=12)

    if len(args) == 2:
        client: Client
        obj: Union[Type[_T], Type[List[_T]]]

        client, obj = args
        if not isinstance(obj, type) and not isinstance(obj, _GenericAlias):
            raise LibraryException(
                message="The object must not be an instance of a class!", code=12
            )

        http_name = f"get_{obj.__name__.lower()}"
        kwarg_name = f"{obj.__name__.lower()}_id"
        if isinstance(obj, _GenericAlias):
            _obj: Type[_T] = get_args(obj)[0]
            _objects: List[_obj] = []
            kwarg_name += "s"

            force_cache = kwargs.pop("force", None) == "cache"
            force_http = kwargs.pop("force", None) == "http"

            if not force_http:
                _objects = get_cache(_obj, _list=True)

            if force_cache:
                return _objects

            elif not force_http and None not in _objects:
                return _return_cache(_objects)

            elif force_http:
                _objects.clear()
                _func = getattr(http_name, client._http)
                for _id in kwargs.get(kwarg_name):
                    _kwargs = kwargs
                    _kwargs.pop(kwarg_name)
                    _kwargs[kwarg_name[:-1]] = _id
                    _objects.append(_func(**_kwargs))
                return _http_request(_obj, http=client._http, request=_objects)

            else:
                _func = getattr(http_name, client._http)
                for _index, __obj in enumerate(_objects):
                    if __obj is None:
                        _id = kwargs.get(kwarg_name)[_index]
                        _kwargs = kwargs
                        _kwargs.pop(kwarg_name)
                        _kwargs[kwarg_name[:-1]] = _id
                        _request = _func(**_kwargs)
                        _objects[_index] = _request
                return _http_request(_obj, http=client._http, request=_objects)

        _obj: _T = None

        force_cache = kwargs.pop("force", None) == "cache"
        force_http = kwargs.pop("force", None) == "http"
        if not force_http:
            _obj = get_cache(obj)

        if force_cache:
            return _obj

        elif not force_http and _obj:
            return _return_cache(_obj)

        else:
            return _http_request(
                obj=obj, http=client._http, request=None, _name=http_name, **kwargs
            )

    elif len(args) == 1:
        return search_iterable(*args, **kwargs)


async def _http_request(
    obj: Type[_T],
    http: HTTPClient,
    request: Union[Coroutine, List[Union[_T, Coroutine]], List[Coroutine]] = None,
    _name: str = None,
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


async def _return_cache(obj: _T) -> _T:
    await sleep(0)  # iirc Bluenix meant that any coroutine should await at least once
    return obj
