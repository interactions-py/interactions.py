import time
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from interactions.models.discord.snowflake import Snowflake_Type, Snowflake

__all__ = ("TimestampStyles", "Timestamp")

DISCORD_EPOCH = 1420070400000


class TimestampStyles(str, Enum):
    ShortTime = "t"
    LongTime = "T"
    ShortDate = "d"
    LongDate = "D"
    ShortDateTime = "f"  # default
    LongDateTime = "F"
    RelativeTime = "R"

    def __str__(self) -> str:
        return self.value


class Timestamp(datetime):
    """
    A special class that represents Discord timestamps.

    Assumes that all naive datetimes are based on local timezone.

    """

    @classmethod
    def fromdatetime(cls, dt: datetime) -> "Timestamp":
        """Construct a timezone-aware UTC datetime from a datetime object."""
        timestamp = cls.fromtimestamp(dt.timestamp(), tz=dt.tzinfo)

        return timestamp.astimezone() if timestamp.tzinfo is None else timestamp

    @classmethod
    def utcfromtimestamp(cls, t: float) -> "Timestamp":
        """Construct a timezone-aware UTC datetime from a POSIX timestamp."""
        return super().utcfromtimestamp(t).replace(tzinfo=timezone.utc)

    @classmethod
    def fromisoformat(cls, date_string: str) -> "Timestamp":
        timestamp = super().fromisoformat(date_string)

        return timestamp.astimezone() if timestamp.tzinfo is None else timestamp

    @classmethod
    def fromisocalendar(cls, year: int, week: int, day: int) -> "Timestamp":
        return super().fromisocalendar(year, week, day).astimezone()

    @classmethod
    def fromtimestamp(cls, t: float, tz=None) -> "Timestamp":
        try:
            timestamp = super().fromtimestamp(t, tz=tz)
        except Exception:
            # May be in milliseconds instead of seconds
            timestamp = super().fromtimestamp(t / 1000, tz=tz)

        return timestamp.astimezone() if timestamp.tzinfo is None else timestamp

    @classmethod
    def fromordinal(cls, n: int) -> "Timestamp":
        return super().fromordinal(n).astimezone()

    @classmethod
    def now(cls, tz=None) -> "Timestamp":
        """
        Construct a datetime from time.time() and optional time zone info.

        If no timezone is provided, the time is assumed to be from the computer's
        local timezone.
        """
        t = time.time()
        return cls.fromtimestamp(t, tz)

    @classmethod
    def utcnow(cls) -> "Timestamp":
        """Construct a timezone-aware UTC datetime from time.time()."""
        t = time.time()
        return cls.utcfromtimestamp(t)

    def to_snowflake(self, high: bool = False) -> Union[str, "Snowflake"]:
        """
        Returns a numeric snowflake pretending to be created at the given date.

        When using as the lower end of a range, use ``tosnowflake(high=False) - 1``
        to be inclusive, ``high=True`` to be exclusive.
        When using as the higher end of a range, use ``tosnowflake(high=True) + 1``
        to be inclusive, ``high=False`` to be exclusive

        """
        discord_millis = int(self.timestamp() * 1000 - DISCORD_EPOCH)
        return (discord_millis << 22) + (2**22 - 1 if high else 0)

    @classmethod
    def from_snowflake(cls, snowflake: "Snowflake_Type") -> "Timestamp":
        """
        Construct a timezone-aware UTC datetime from a snowflake.

        Args:
            snowflake: The snowflake to convert.

        Returns:
            A timezone-aware UTC datetime.

        ??? Info
            https://discord.com/developers/docs/reference#convert-snowflake-to-datetime

        """
        if isinstance(snowflake, str):
            snowflake = int(snowflake)

        timestamp = ((snowflake >> 22) + DISCORD_EPOCH) / 1000
        return cls.utcfromtimestamp(timestamp)

    def format(self, style: Optional[Union[TimestampStyles, str]] = None) -> str:
        """
        Format the timestamp for discord client to display.

        Args:
            style: The style to format the timestamp with.

        Returns:
            The formatted timestamp.

        """
        return f"<t:{self.timestamp():.0f}:{style}>" if style else f"<t:{self.timestamp():.0f}>"

    def __str__(self) -> str:
        return self.format()
