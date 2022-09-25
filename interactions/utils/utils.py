from asyncio import Task, get_running_loop, sleep
from functools import wraps
from math import inf
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    Coroutine,
    Iterable,
    List,
    Optional,
    TypeVar,
    Union,
)

from ..api.error import LibraryException
from ..client.models.component import ActionRow, Button, Component, SelectMenu
from .missing import MISSING

if TYPE_CHECKING:
    from ..api.http.client import HTTPClient
    from ..api.models.channel import AsyncHistoryIterator, Channel
    from ..api.models.guild import AsyncMembersIterator, Guild
    from ..api.models.member import Member
    from ..api.models.message import Message
    from ..api.models.misc import Snowflake
    from ..client.bot import Client, Extension
    from ..client.context import CommandContext  # noqa F401

__all__ = (
    "autodefer",
    "spread_to_rows",
    "search_iterable",
    "disable_components",
    "get_channel_history",
)

_T = TypeVar("_T")


def autodefer(
    delay: Union[float, int] = 2,
    ephemeral: bool = False,
    edit_origin: bool = False,
) -> Callable[[Callable[..., Union[Awaitable, Coroutine]]], Callable[..., Awaitable]]:
    """
    A decorator that automatically defers a command if it did not respond within ``delay`` seconds.

    The structure of the decorator is:

    .. code-block:: python

        @bot.command()
        @autodefer()  # configurable
        async def command(ctx):
            await asyncio.sleep(5)
            await ctx.send("I'm awake now!")

    :param delay?: The amount of time in seconds to wait before defering the command. Defaults to ``2`` seconds.
    :type delay?: Union[float, int]
    :param ephemeral?: Whether the command is deferred ephemerally. Defaults to ``False``.
    :type ephemeral?: bool
    :param edit_origin?: Whether the command is deferred on origin. Defaults to ``False``.
    :type edit_origin?: bool
    :return: The inner function, for decorating.
    :rtype:
    """

    def decorator(coro: Callable[..., Union[Awaitable, Coroutine]]) -> Callable[..., Awaitable]:
        from ..client.context import CommandContext, ComponentContext  # noqa F811

        @wraps(coro)
        async def deferring_func(
            ctx: Union["CommandContext", "ComponentContext", "Extension"], *args, **kwargs
        ):
            try:
                loop = get_running_loop()
            except RuntimeError as e:
                raise RuntimeError("No running event loop detected!") from e

            if args and isinstance(args[0], (ComponentContext, CommandContext)):
                self = ctx
                args = list(args)
                ctx = args.pop(0)

                task: Task = loop.create_task(coro(self, ctx, *args, **kwargs))
            else:
                task: Task = loop.create_task(coro(ctx, *args, **kwargs))

            await sleep(delay)

            if task.done():
                return task.result()

            if not (ctx.deferred or ctx.responded):
                if isinstance(ctx, ComponentContext):
                    await ctx.defer(ephemeral=ephemeral, edit_origin=edit_origin)
                else:
                    await ctx.defer(ephemeral=ephemeral)

            return await task

        return deferring_func

    return decorator


def spread_to_rows(
    *components: Union[ActionRow, Button, SelectMenu], max_in_row: int = 5
) -> List[ActionRow]:
    r"""
    A helper function that spreads components into :class:`ActionRow` s.

    Example:

    .. code-block:: python

        @bot.command()
        async def command(ctx):
            b1 = Button(style=1, custom_id="b1", label="b1")
            b2 = Button(style=1, custom_id="b2", label="b2")
            s1 = SelectMenu(
                custom_id="s1",
                options=[
                    SelectOption(label="1", value="1"),
                    SelectOption(label="2", value="2"),
                ],
            )
            b3 = Button(style=1, custom_id="b3", label="b3")
            b4 = Button(style=1, custom_id="b4", label="b4")

            await ctx.send("Components:", components=spread_to_rows(b1, b2, s1, b3, b4))

    .. note::
        You can only pass in :class:`ActionRow`s, :class:`Button`s, and :class:`SelectMenu`s, but in any order.

    :param \*components: The components to spread.
    :type \*components: Union[ActionRow, Button, SelectMenu]
    :param max_in_row?: The maximum number of components in a single row. Defaults to ``5``.
    :type max_in_row?: int
    """
    if not components or len(components) > 25:
        raise LibraryException(code=12, message="Number of components should be between 1 and 25.")
    if not 1 <= max_in_row <= 5:
        raise LibraryException(code=12, message="max_in_row should be between 1 and 5.")

    rows: List[ActionRow] = []
    action_row: List[Union[Button, SelectMenu]] = []

    for component in list(components):
        if component is not None and isinstance(component, Button):
            action_row.append(component)

            if len(action_row) == max_in_row:
                rows.append(ActionRow(components=action_row))
                action_row = []

            continue

        if action_row:
            rows.append(ActionRow(components=action_row))
            action_row = []

        if component is not None:
            if isinstance(component, ActionRow):
                rows.append(component)
            elif isinstance(component, SelectMenu):
                rows.append(ActionRow(components=[component]))

    if action_row:
        rows.append(ActionRow(components=action_row))

    if len(rows) > 5:
        raise LibraryException(code=12, message="Number of rows exceeds 5.")

    return rows


def search_iterable(
    iterable: Iterable[_T], check: Optional[Callable[[_T], bool]] = None, /, **kwargs
) -> List[_T]:
    """
    Searches through an iterable for items that:
    - Are True for the check, if one is given
    - Have attributes that match the keyword arguments (e.x. passing `id=your_id` will only return objects with that id)

    :param iterable: The iterable to search through
    :type iterable: Iterable
    :param check: The check that items will be checked against
    :type check: Callable[[Any], bool]
    :param kwargs: Any attributes the items should have
    :type kwargs: Any
    :return: All items that match the check and keywords
    :rtype: list
    """
    if check:
        iterable = filter(check, iterable)

    if kwargs:
        iterable = filter(
            lambda item: all(getattr(item, attr) == value for attr, value in kwargs.items()),
            iterable,
        )

    return list(iterable)


def disable_components(
    components: Union[
        List[Component],
        List[ActionRow],
        List[Button],
        List[SelectMenu],
        ActionRow,
        Component,
        Button,
        SelectMenu,
    ]
) -> None:
    """
    Disables the given components.

    :param components: The components to disable
    :type components: Union[List[Component], List[ActionRow], List[Button], List[SelectMenu], ActionRow, Component, Button, SelectMenu]
    """
    if isinstance(components, (Component, ActionRow)):
        for component in components.components:
            component.disabled = True
    elif isinstance(components, (Button, SelectMenu)):
        components.disabled = True
    elif isinstance(components, list):
        if not all(
            isinstance(component, (Button, SelectMenu)) for component in components
        ) or not all(isinstance(component, (ActionRow, Component)) for component in components):
            raise LibraryException(
                12,
                "You must only specify lists of 'Buttons' and 'SelectMenus' or 'ActionRow' and 'Component'",
            )
        if isinstance(components[0], (Button, SelectMenu)):
            for component in components:
                component.disabled = True

        elif isinstance(components[0], (ActionRow, Component)):
            components: List[ActionRow, Component]
            for _components in components:
                for component in _components.components:
                    component.disabled = True


def get_channel_history(
    http: Union["HTTPClient", "Client"],
    channel: Union[int, str, "Snowflake", "Channel"],
    start_at: Optional[Union[int, str, "Snowflake", "Message"]] = MISSING,
    reverse: Optional[bool] = False,
    check: Optional[Callable[["Message"], bool]] = None,
    maximum: Optional[int] = inf,
) -> "AsyncHistoryIterator":
    """
    Gets the history of a channel.

    :param http: The HTTPClient of the bot or your bot instance
    :type http: Union[HTTPClient, Client]
    :param channel: The channel to get the history from
    :type channel: Union[int, str, Snowflake, Channel]
    :param start_at?: The message to begin getting the history from
    :type start_at?: Optional[Union[int, str, Snowflake, Message]]
    :param reverse?: Whether to only get newer message. Default False
    :type reverse?: Optional[bool]
    :param check?: A check to ignore specific messages
    :type check?: Optional[Callable[[Message], bool]]
    :param maximum?: A set maximum of messages to get before stopping the iteration
    :type maximum?: Optional[int]

    :return: An asynchronous iterator over the history of the channel
    :rtype: AsyncHistoryIterator
    """
    from ..api.models.channel import AsyncHistoryIterator

    return AsyncHistoryIterator(
        http if not hasattr(http, "_http") else http._http,
        channel,
        start_at=start_at,
        reverse=reverse,
        check=check,
        maximum=maximum,
    )


def get_guild_members(
    http: Union["HTTPClient", "Client"],
    guild: Union[int, str, "Snowflake", "Guild"],
    start_at: Optional[Union[int, str, "Snowflake", "Member"]] = MISSING,
    check: Optional[Callable[["Member"], bool]] = None,
    maximum: Optional[int] = inf,
) -> "AsyncMembersIterator":
    """
    Gets the members of a guild

    :param http: The HTTPClient of the bot or your bot instance
    :type http: Union[HTTPClient, Client]
    :param guild: The channel to get the history from
    :type guild: Union[int, str, Snowflake, Guild]
    :param start_at?: The message to begin getting the history from
    :type start_at?: Optional[Union[int, str, Snowflake, Member]]
    :param check?: A check to ignore specific messages
    :type check?: Optional[Callable[[Member], bool]]
    :param maximum?: A set maximum of members to get before stopping the iteration
    :type maximum?: Optional[int]

    :return: An asynchronous iterator over the history of the channel
    :rtype: AsyncMembersIterator
    """
    from ..api.models.guild import AsyncMembersIterator

    return AsyncMembersIterator(
        http if not hasattr(http, "_http") else http._http,
        guild,
        start_at=start_at,
        maximum=maximum,
        check=check,
    )
