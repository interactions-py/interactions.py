from asyncio import Task, get_running_loop, sleep
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Union

from ...api.error import LibraryException
from .component import ActionRow, Button, SelectMenu

if TYPE_CHECKING:
    from ..context import CommandContext


__all__ = ["autodefer", "spread_to_rows"]


def autodefer(
    delay: Optional[Union[float, int]] = 2,
    ephemeral: Optional[bool] = False,
    edit_origin: Optional[bool] = False,
):  # TODO: test this out
    """
    docstring
    """  # TODO: change docstring

    def inner(func: Callable[..., Any]) -> Callable[..., Any]:
        from ..context import ComponentContext

        @wraps(func)
        async def deferring_func(ctx: Union["CommandContext", "ComponentContext"], *args, **kwargs):
            try:
                loop = get_running_loop()
            except RuntimeError as e:
                raise RuntimeError("No running event loop detected!") from e
            task: Task = loop.create_task(func(ctx, *args, **kwargs))

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

    return inner


def spread_to_rows(
    *components: Union[ActionRow, Button, SelectMenu], max_in_row: int = 5
) -> List[ActionRow]:  # TODO: test this out
    """
    docstring
    """  # TODO: change docstring
    if not components or len(components) > 25:
        raise LibraryException(code=12, message="Number of components should be between 1 and 25.")
    if not 1 <= max_in_row <= 5:
        raise ValueError(code=12, message="max_in_row should be between 1 and 5.")

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
