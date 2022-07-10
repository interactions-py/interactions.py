from asyncio import sleep
from enum import Enum
from inspect import isawaitable, isfunction
from logging import getLogger
from typing import Coroutine, Iterable, List, Optional, Type, TypeVar, Union, get_args

try:
    from typing import _GenericAlias

except ImportError:
    from typing import _BaseGenericAlias as _GenericAlias

from sys import version_info

from ..api.error import LibraryException
from ..api.http.client import HTTPClient
from ..api.models.channel import Channel
from ..api.models.guild import Guild
from ..api.models.member import Member
from ..api.models.message import Emoji, Message, Sticker
from ..api.models.misc import Snowflake
from ..api.models.role import Role
from ..api.models.user import User
from ..api.models.webhook import Webhook
from .bot import Client

log = getLogger("get")

_A = TypeVar("_A", Channel, Guild, Webhook, User, Sticker, Message, Emoji, Role, Message)

__all__ = (
    "get",
    "Force",
)


class Force(str, Enum):
    """
    An enum representing the force types for the get method.

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
            * based of any other attribute the object inside the iterable has

    The method has to be awaited when:
        * You don't force anything
        * You force HTTP
    The method doesn't have to be awaited when:
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

    Getting from an iterable:

        .. code-block:: python

            # Getting an object from an iterable
            check = lambda role: return role.name == "ADMIN" and role.color == 0xff0000
            roles = [
                interactions.Role(name="NOT ADMIN", color=0xff0000),
                interactions.Role(name="ADMIN", color=0xff0000),
            ]
            role = get(roles, check=check)
            # role will be `interactions.Role(name="ADMIN", color=0xff0000)`

        You can specify *any* attribute to check that the object could have (although only ``check``, ``id`` and
        ``name`` are type-hinted) and the method will check for a match.

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
            called ``parent_id`` bcause ``guild_or_channel_id`` would be horrible to type out every time.

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
            return obj == list[get_args(obj)[0]]

    else:

        def _check():
            return False

    if len(args) == 2 and any(isinstance(_, Iterable) for _ in args):
        raise LibraryException(message="You can only use Iterables as single-argument!", code=12)

    if len(args) == 2:

        client, obj = args
        if not isinstance(obj, type) and not isinstance(obj, _GenericAlias):
            client: Client
            obj: Union[Type[_A], Type[List[_A]]]
            raise LibraryException(
                message="The object must not be an instance of a class!", code=12
            )

        kwargs = _resolve_kwargs(obj, **kwargs)
        http_name = f"get_{obj.__name__.lower()}"
        kwarg_name = f"{obj.__name__.lower()}_id"
        if isinstance(obj, _GenericAlias) or _check():
            _obj: Type[_A] = get_args(obj)[0]
            _objects: List[Union[_obj, Coroutine]] = []
            kwarg_name += "s"

            force_cache = kwargs.pop("force", None) == "cache"
            force_http = kwargs.pop("force", None) == "http"

            if not force_http:
                _objects = _get_cache(_obj, client, kwarg_name, _list=True, **kwargs)

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

        _obj: Optional[_A] = None

        force_cache = kwargs.pop("force", None) == "cache"
        force_http = kwargs.pop("force", None) == "http"
        if not force_http:
            _obj = _get_cache(obj, client, kwarg_name, **kwargs)

        if force_cache:
            return _obj

        elif not force_http and _obj:
            return _return_cache(_obj)

        else:
            return _http_request(obj=obj, http=client._http, _name=http_name, **kwargs)

    elif len(args) == 1:
        return _search_iterable(*args, **kwargs)


async def _http_request(
    obj: Type[_A],
    http: HTTPClient,
    request: Union[Coroutine, List[Union[_A, Coroutine]], List[Coroutine]] = None,
    _name: str = None,
    **kwargs,
) -> Union[_A, List[_A]]:

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


async def _return_cache(
    obj: Union[Optional[_A], List[Optional[_A]]]
) -> Union[Optional[_A], List[Optional[_A]]]:
    await sleep(0)  # iirc Bluenix meant that any coroutine should await at least once
    return obj


def _get_cache(
    _object: Type[_A], client: Client, kwarg_name: str, _list: bool = False, **kwargs
) -> Union[Optional[_A], List[Optional[_A]]]:

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
            _obj.extend(client.cache[_object].get(item) for item in _values)

        else:
            _obj.extend(
                client.cache[_object].get(Snowflake(_id), None) for _id in kwargs.get(kwarg_name)
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


def _search_iterable(items: Iterable[_A], **kwargs) -> Optional[_A]:

    if not isinstance(items, Iterable):
        raise LibraryException(message="The specified items must be an iterable!", code=12)

    if not kwargs:
        raise LibraryException(
            message="You have to specify either a custom check or a keyword argument to check against!",
            code=12,
        )

    if len(list(kwargs)) > 1:
        raise LibraryException(
            message="Only one keyword argument to check against is allowed!", code=12
        )

    _arg = str(list(kwargs)[0])

    __obj = next(
        (
            item
            for item in items
            if (
                str(getattr(item, _arg, None)) == str(kwargs.get(_arg))
                if not isfunction(kwargs.get(_arg))
                else kwargs.get(_arg)(item)
            )
        ),
        None,
    )
    return __obj


def _resolve_kwargs(obj, **kwargs):
    # This function is needed to get correct kwarg names
    if __id := kwargs.pop("parent_id", None):
        kwargs[f"{'channel_id' if obj in [Message, List[Message]] else 'guild_id'}"] = __id

    if __id := kwargs.pop("object_id", None):
        _kwarg_name = f"{obj.__name__.lower()}_id"
        kwargs[_kwarg_name] = __id

    elif __id := kwargs.pop("object_ids", None):
        _kwarg_name = f"{get_args(obj)[0].__name__.lower()}_ids"
        kwargs[_kwarg_name] = __id

    else:
        raise LibraryException(code=12, message="The specified kwargs are invalid!")

    return kwargs
