from typing import Union, TYPE_CHECKING

import interactions.api.events as events
from interactions.models import User, Member, BaseChannel, Timestamp, to_snowflake, Activity
from interactions.models.discord.enums import Status
from ._template import EventMixinTemplate, Processor

if TYPE_CHECKING:
    from interactions.api.events import RawGatewayEvent

__all__ = ("UserEvents",)


class UserEvents(EventMixinTemplate):
    @Processor.define()
    async def _on_raw_typing_start(self, event: "RawGatewayEvent") -> None:
        """
        Process raw typing start and dispatch a processed typing event.

        Args:
            event: raw typing start event

        """
        author: Union[User, Member]
        channel: BaseChannel
        guild = None

        if member := event.data.get("member"):
            author = self.cache.place_member_data(event.data.get("guild_id"), member)
            guild = await self.cache.fetch_guild(event.data.get("guild_id"))
        else:
            author = await self.cache.fetch_user(event.data.get("user_id"))

        channel = await self.cache.fetch_channel(event.data.get("channel_id"))

        self.dispatch(
            events.TypingStart(
                author=author,
                channel=channel,
                guild=guild,
                timestamp=Timestamp.utcfromtimestamp(event.data.get("timestamp")),
            )
        )

    @Processor.define()
    async def _on_raw_presence_update(self, event: "RawGatewayEvent") -> None:
        """
        Process raw presence update and dispatch a processed presence update event.

        Args:
            event: raw presence update event

        """
        g_id = to_snowflake(event.data["guild_id"])
        if user := self.cache.get_user(event.data["user"]["id"]):
            user.status = Status[event.data["status"].upper()]
            user.activities = Activity.from_list(event.data.get("activities"))

            self.dispatch(
                events.PresenceUpdate(user, user.status, user.activities, event.data.get("client_status", None), g_id)
            )
