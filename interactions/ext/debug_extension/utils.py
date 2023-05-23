import datetime
import inspect
import weakref
from typing import TYPE_CHECKING, Any, Optional, Union

from interactions.client.utils.cache import TTLCache, NullCache
from interactions.models import Embed, MaterialColors

if TYPE_CHECKING:
    from interactions.client import Client

__all__ = ("debug_embed", "get_cache_state", "strf_delta")


def debug_embed(title: str, **kwargs) -> Embed:
    """Create a debug embed with a standard header and footer."""
    e = Embed(
        f"I.py Debug: {title}",
        url="https://github.com/interactions-py/interactions.py",
        color=MaterialColors.BLUE_GREY,
        **kwargs,
    )
    e.set_footer(
        "I.py Debug Extension",
        icon_url="https://media.discordapp.net/attachments/907639005070377020/918600896433238097/sparkle-snekCUnetnoise_scaleLevel0x2.500000.png",
    )
    return e


def get_cache_state(bot: "Client") -> str:
    """Create a nicely formatted table of internal cache state."""
    caches = {
        c[0]: getattr(bot.cache, c[0])
        for c in inspect.getmembers(bot.cache, predicate=lambda x: isinstance(x, dict))
        if not c[0].startswith("__")
    }
    caches["endpoints"] = bot.http._endpoints
    caches["rate_limits"] = bot.http.ratelimit_locks
    table = []

    for cache, val in caches.items():
        if isinstance(val, TTLCache):
            amount = [len(val), f"{val.hard_limit}({val.soft_limit})"]
            expire = f"{val.ttl}s"
        elif isinstance(val, NullCache):
            amount = ("DISABLED",)
            expire = "N/A"
        elif isinstance(val, (weakref.WeakValueDictionary, weakref.WeakKeyDictionary)):
            amount = [len(val), "∞"]
            expire = "w_ref"
        else:
            amount = [len(val), "∞"]
            expire = "none"

        row = [cache.removesuffix("_cache"), amount, expire]
        table.append(row)

    adjust_subcolumn(table, 1, aligns=[">", "<"])

    labels = ["Cache", "Amount", "Expire"]
    return make_table(table, labels)


def strf_delta(time_delta: datetime.timedelta, show_seconds: bool = True) -> str:
    """Formats timedelta into a human readable string."""
    years, days = divmod(time_delta.days, 365)
    hours, rem = divmod(time_delta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)

    years_fmt = f"{years} year{'s' if years > 1 or years == 0 else ''}"
    days_fmt = f"{days} day{'s' if days > 1 or days == 0 else ''}"
    hours_fmt = f"{hours} hour{'s' if hours > 1 or hours == 0 else ''}"
    minutes_fmt = f"{minutes} minute{'s' if minutes > 1 or minutes == 0 else ''}"
    seconds_fmt = f"{seconds} second{'s' if seconds > 1 or seconds == 0 else ''}"

    if years >= 1:
        return f"{years_fmt} and {days_fmt}"
    if days >= 1:
        return f"{days_fmt} and {hours_fmt}"
    if hours >= 1:
        return f"{hours_fmt} and {minutes_fmt}"
    return f"{minutes_fmt} and {seconds_fmt}" if show_seconds else f"{minutes_fmt}"


def _make_solid_line(
    column_widths: list[int],
    left_char: str,
    middle_char: str,
    right_char: str,
) -> str:
    """
    Internal helper function.

    Constructs a "solid" line for the table (top, bottom, line between labels and table)
    """
    return f"{left_char}{middle_char.join('─' * (width + 2) for width in column_widths)}{right_char}"


def _make_data_line(
    column_widths: list[int],
    line: list[Any],
    left_char: str,
    middle_char: str,
    right_char: str,
    aligns: Union[list[str], str] = "<",
) -> str:
    """
    Internal helper function.

    Constructs a line with data for the table
    """
    if isinstance(aligns, str):
        aligns = [aligns for _ in column_widths]

    line = (f"{value!s: {align}{width}}" for width, align, value in zip(column_widths, aligns, line, strict=False))
    return f"{left_char}{f'{middle_char}'.join(line)}{right_char}"


def _get_column_widths(columns) -> list[int]:
    """
    Internal helper function.

    Calculates max width of each column
    """
    return [max(len(str(value)) for value in column) for column in columns]


def adjust_subcolumn(
    rows: list[list[Any]],
    column_index: int,
    separator: str = "/",
    aligns: Union[list[str], str] = "<",
) -> None:
    """Converts column composed of list of subcolumns into aligned str representation."""
    column = list(zip(*rows, strict=False))[column_index]
    subcolumn_widths = _get_column_widths(zip(*column, strict=False))
    if isinstance(aligns, str):
        aligns = [aligns for _ in subcolumn_widths]

    column = [_make_data_line(subcolumn_widths, row, "", separator, "", aligns) for row in column]
    for row, new_item in zip(rows, column, strict=False):
        row[column_index] = new_item


def make_table(rows: list[list[Any]], labels: Optional[list[Any]] = None, centered: bool = False) -> str:
    """
    Converts 2D list to str representation as table

    :param rows: 2D list containing objects that have a single-line representation (via `str`). All rows must be of the same length.
    :param labels: List containing the column labels. If present, the length must equal to that of each row.
    :param centered: If the items should be aligned to the center, else they are left aligned.
    :return: A table representing the rows passed in.
    """
    columns = zip(*rows, strict=False) if labels is None else zip(*rows, labels, strict=False)
    column_widths = _get_column_widths(columns)
    align = "^" if centered else "<"
    align = [align for _ in column_widths]

    lines = [_make_solid_line(column_widths, "╭", "┬", "╮")]

    data_left = "│ "
    data_middle = " │ "
    data_right = " │"
    if labels is not None:
        lines.append(_make_data_line(column_widths, labels, data_left, data_middle, data_right, align))
        lines.append(_make_solid_line(column_widths, "├", "┼", "┤"))
    lines.extend(_make_data_line(column_widths, row, data_left, data_middle, data_right, align) for row in rows)
    lines.append(_make_solid_line(column_widths, "╰", "┴", "╯"))
    return "\n".join(lines)
