import re
from typing import TYPE_CHECKING

import attrs

import interactions.models as models
from interactions.client.const import MISSING, AsyncCallable
from interactions.client.utils.attr_utils import docs
from interactions.models.discord.snowflake import to_snowflake

if TYPE_CHECKING:
    from interactions.client.client import Client
    from interactions.models.discord.snowflake import Snowflake_Type
    from interactions.models.discord.guild import Guild

__all__ = ("BaseEvent", "GuildEvent", "RawGatewayEvent")

_event_reg = re.compile("(?<!^)(?=[A-Z])")


@attrs.define(eq=False, order=False, hash=False, slots=False, kw_only=False)
class BaseEvent:
    """A base event that all other events inherit from."""

    override_name: str = attrs.field(repr=False, kw_only=True, default=None)
    """Custom name of the event to be used when dispatching."""
    bot: "Client" = attrs.field(repr=False, kw_only=True, default=MISSING)
    """The client instance that dispatched this event."""

    @property
    def client(self) -> "Client":
        """The client instance that dispatched this event."""
        return self.bot

    @property
    def resolved_name(self) -> str:
        """The name of the event, defaults to the class name if not overridden."""
        name = self.override_name or self.__class__.__name__
        return _event_reg.sub("_", name).lower()

    @classmethod
    def listen(cls, coro: AsyncCallable, client: "Client") -> "models.Listener":
        """
        A shortcut for creating a listener for this event

        Args:
            coro: The coroutine to call when the event is triggered.
            client: The client instance to listen to.


        ??? Hint "Example Usage:"
            ```python
            class SomeClass:
                def __init__(self, bot: Client):
                    Ready.listen(self.some_func, bot)

                async def some_func(self, event):
                    print(f"{event.resolved_name} triggered")
            ```
        Returns:
            A listener object.
        """
        listener = models.Listener.create(cls().resolved_name)(coro)
        client.add_listener(listener)
        return listener


@attrs.define(eq=False, order=False, hash=False, slots=False, kw_only=False)
class GuildEvent(BaseEvent):
    """A base event that adds guild_id."""

    guild_id: "Snowflake_Type" = attrs.field(repr=False, metadata=docs("The ID of the guild"), converter=to_snowflake)

    @property
    def guild(self) -> "Guild":
        """Guild related to event"""
        return self.bot.cache.get_guild(self.guild_id)


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class RawGatewayEvent(BaseEvent):
    """
    An event dispatched from the gateway.

    Holds the raw dict that the gateway dispatches

    """

    data: dict = attrs.field(repr=False, factory=dict)
    """Raw Data from the gateway"""
