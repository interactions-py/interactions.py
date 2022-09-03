from asyncio import sleep
from enum import Enum
from inspect import isawaitable
from logging import getLogger
from typing import TYPE_CHECKING, Coroutine, List, Optional, Type, TypeVar, Union, get_args

try:
    from typing import _GenericAlias

except ImportError:
    from typing import _BaseGenericAlias as _GenericAlias

from sys import version_info

from ..api.error import LibraryException
from ..api.models.emoji import Emoji
from ..api.models.member import Member
from ..api.models.message import Message
from ..api.models.misc import Snowflake
from ..api.models.role import Role

log = getLogger("get")

_T = TypeVar("_T")

if TYPE_CHECKING:
    from ..api.http.client import HTTPClient
    from ..client.bot import Client

__all__ = (
    "get",
    "Force",
)


class Force(str, Enum):
    """
    An enumerable object representing the force types for the get method.

    :ivar str CACHE: Enforce the usage of cache and block the usage of http
    :ivar str HTTP: Enforce the usage of http and block the usage of cache
    """

    CACHE = "cache"
    HTTP = "http"


def get(client: "Client", obj: Type[_T], **kwargs) -> Optional[_T]:
    """
    Helper method to get an object.

    This method can do the following:
        * Get a list of specific objects
            * purely from cache
            * purely from HTTP
            * from cache and additionally from HTTP for every ID that was not found in cache
        * Get a single specific object
            * purely from cache
            * purely from HTTP
            * from HTTP if not found in cache else from cache

    The method has to be awaited when:
        * You don't force anything
        * You force HTTP
    The method doesn't have to be awaited when:
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

    Getting an object:

        Here you will see two examples on how to get a single objects and the variations of how the object can be
        gotten.

        * Example 1/2: Getting a Channel:

            .. code-block:: python

                # normally
                channel = await get(client, interactions.Channel, object_id=your_channel_id)
                # always has a value

                # with http force
                channel = await get(client, interactions.Channel, object_id=your_channel_id, force="http")
                # always has a value

                # with cache force
                channel = get(client, interactions.Channel, object_id=your_channel_id, force="cache")
                # because of cache only, this can be None


        * Example 2/2: Getting a Member:

            .. code-block:: python

                # normally
                member = await get(
                    client, interactions.Member, parent_id=your_guild_id, object_id=your_member_id
                )
                # always has a value

                # with http force
                member = await get(
                    client, interactions.Member, parent_id=your_guild_id, object_id=your_member_id
                )
                # always has a value

                # with cache force
                member = await get(
                    client, interactions.Member, parent_id=your_guild_id, object_id=your_member_id
                )
                # because of cache only, this can be None


        Both examples should have given you a basic overview on how to get a single object. Now we will move on with
        lists of objects.

        .. important::
            The ``parent_id`` represents the channel or guild id that belongs to the objects you want to get. It is
            called ``parent_id`` because ``guild_or_channel_id`` would be horrible to type out every time.

    Getting a list of an object:
        Here you will see 1 example of how to get a list of objects. The possibilities on how to force (and their
        results) are the same as in the examples above.

        * Example 1/1: Getting a list of members:

            .. code-block:: python

                from typing import List

                # you can also use `list[interactions.Member]` if you have python >= 3.9

                members = await get(
                    client,
                    List[interactions.Member],
                    parent_id=your_guild_id,
                    object_ids=[your_member_id1, your_member_id2, ...],
                )


        If you enforce cache when getting a list of objects, found objets will be placed into the list and not found
        objects will be placed as ``None`` into the list.

    """

    if version_info >= (3, 9):

        def _check():
            return (
                obj == list[get_args(obj)[0]]
                if isinstance(get_args(obj), tuple) and get_args(obj)
                else False
            )

    else:

        def _check():
            return False

    if not isinstance(obj, type) and not isinstance(obj, _GenericAlias):
        raise LibraryException(message="The object must not be an instance of a class!", code=12)

    client: "Client"
    obj: Union[Type[_T], Type[List[_T]]]
    kwargs = _resolve_kwargs(obj, **kwargs)

    force_arg = kwargs.pop("force", None)
    force_cache = force_arg == "cache"
    force_http = force_arg == "http"

    if isinstance(obj, _GenericAlias) or _check():
        _obj: Type[_T] = get_args(obj)[0]
        http_name = f"get_{_obj.__name__.lower()}"
        kwarg_name = f"{_obj.__name__.lower()}_ids"
        _objects: List[Union[_obj, Coroutine]] = []

        if not force_http:
            _objects = _get_cache(_obj, client, kwarg_name, _list=True, **kwargs)

        if force_cache:
            return _objects

        elif not force_http and None not in _objects:
            return _return_cache(_objects)

        elif force_http:
            _objects.clear()
            _func = getattr(client._http, http_name)
            for _id in kwargs.get(kwarg_name):
                _kwargs = kwargs.copy()
                _kwargs.pop(kwarg_name)
                _kwargs[kwarg_name[:-1]] = _id
                _objects.append(_func(**_kwargs))
            return _http_request(_obj, http=client._http, request=_objects)

        else:
            _func = getattr(client._http, http_name)
            for _index, __obj in enumerate(_objects):
                if __obj is None:
                    _id = kwargs.get(kwarg_name)[_index]
                    _kwargs = kwargs.copy()
                    _kwargs.pop(kwarg_name)
                    _kwargs[kwarg_name[:-1]] = _id
                    _request = _func(**_kwargs)
                    _objects[_index] = _request
            return _http_request(_obj, http=client._http, request=_objects)

    http_name = f"get_{obj.__name__.lower()}"
    kwarg_name = f"{obj.__name__.lower()}_id"

    _obj: Optional[_T] = None

    if not force_http:
        _obj = _get_cache(obj, client, kwarg_name, **kwargs)

    if force_cache:
        return _obj

    elif not force_http and _obj:
        return _return_cache(_obj)

    else:
        return _http_request(obj=obj, http=client._http, _name=http_name, **kwargs)


async def _http_request(
    obj: Type[_T],
    http: "HTTPClient",
    request: Union[Coroutine, List[Union[_T, Coroutine]], List[Coroutine]] = None,
    _name: str = None,
    **kwargs,
) -> Union[_T, List[_T]]:
    if not request:
        if obj in (Role, Emoji):
            from ..api.models.guild import Guild

            _guild = Guild(**await http.get_guild(kwargs.pop("guild_id")), _client=http)
            _func = getattr(_guild, _name)
            return await _func(**kwargs)

        _func = getattr(http, _name)
        _obj = await _func(**kwargs)
        return obj(**_obj, _client=http)

    if not isinstance(request, list):
        return obj(**await request, _client=http)

    return [obj(**await req, _client=http) if isawaitable(req) else req for req in request]


async def _return_cache(
    obj: Union[Optional[_T], List[Optional[_T]]]
) -> Union[Optional[_T], List[Optional[_T]]]:
    await sleep(0)  # iirc Bluenix meant that any coroutine should await at least once
    return obj


def _get_cache(
    _object: Type[_T], client: "Client", kwarg_name: str, _list: bool = False, **kwargs
) -> Union[Optional[_T], List[Optional[_T]]]:
    if _list:
        _obj = []
        if _object == Member:  # Can't be more dynamic on this
            _guild_id = Snowflake(kwargs.get("guild_id"))
            _values = [
                (
                    _guild_id,
                    Snowflake(_id),
                )
                for _id in kwargs.get("member_ids")
            ]
            _obj.extend(client._http.cache[_object].get(item, None) for item in _values)

        else:
            _obj.extend(
                client._http.cache[_object].get(Snowflake(_id), None)
                for _id in kwargs.get(kwarg_name)
            )
    else:
        if _object == Member:
            _values = (
                Snowflake(kwargs.get("guild_id")),
                Snowflake(kwargs.get("member_id")),
            )  # Fuck it, I can't be dynamic on this
        else:
            _values = Snowflake(kwargs.get(kwarg_name))

        _obj = client._http.cache[_object].get(_values)
    return _obj


def _resolve_kwargs(obj, **kwargs):
    # This function is needed to get correct kwarg names
    if __id := kwargs.pop("parent_id", None):

        if version_info >= (3, 9):
            _list = [Message, List[Message], list[Message]]
        else:
            _list = [Message, List[Message]]

        kwargs[f"{'channel_id' if obj in _list else 'guild_id'}"] = __id

    if __id := kwargs.pop("object_id", None):
        _kwarg_name = f"{obj.__name__.lower()}_id"
        kwargs[_kwarg_name] = __id

    elif __id := kwargs.pop("object_ids", None):
        _kwarg_name = f"{get_args(obj)[0].__name__.lower()}_ids"
        kwargs[_kwarg_name] = __id

    else:
        raise LibraryException(code=12, message="The specified kwargs are invalid!")

    return kwargs
