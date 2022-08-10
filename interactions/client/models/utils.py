from asyncio import Task, get_running_loop, sleep
from functools import wraps
from inspect import getfullargspec
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

from ...api.error import LibraryException
from .component import ActionRow, Button, SelectMenu

if TYPE_CHECKING:
    from ..context import CommandContext

__all__ = ("autodefer", "spread_to_rows", "search_iterable")

_T = TypeVar("_T")


def autodefer(
    delay: Union[float, int] = 2,
    ephemeral: bool = False,
    edit_origin: bool = False,
) -> Callable[[Callable[..., Awaitable]], Callable[..., Awaitable]]:
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
        from ..context import ComponentContext

        @wraps(coro)
        async def deferring_func(
            ctx: Union["CommandContext", "ComponentContext"], *args: tuple, **kwargs
        ):
            try:
                loop = get_running_loop()
            except RuntimeError as e:
                raise RuntimeError("No running event loop detected!") from e

            if "self" in getfullargspec(coro).args:
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
