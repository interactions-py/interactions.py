from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import attrs

from interactions.client.const import MISSING, Absent
from interactions.client.errors import EventLocationNotProvided
from interactions.client.utils import to_image_data
from interactions.client.utils.attr_converters import optional
from interactions.client.utils.attr_converters import timestamp_converter
from interactions.models.discord.asset import Asset
from interactions.models.discord.file import UPLOADABLE_TYPE
from interactions.models.discord.snowflake import Snowflake_Type, to_snowflake
from interactions.models.discord.timestamp import Timestamp
from .base import DiscordObject
from .enums import ScheduledEventPrivacyLevel, ScheduledEventType, ScheduledEventStatus

if TYPE_CHECKING:
    from interactions.client.client import Client
    from interactions.models.discord.channel import GuildStageVoice, GuildVoice
    from interactions.models.discord.guild import Guild
    from interactions.models.discord.user import Member
    from interactions.models.discord.user import User

__all__ = ("ScheduledEvent",)


@attrs.define(eq=False, order=False, hash=False, kw_only=True)
class ScheduledEvent(DiscordObject):
    name: str = attrs.field(repr=True)
    description: str = attrs.field(repr=False, default=MISSING)
    entity_type: Union[ScheduledEventType, int] = attrs.field(repr=False, converter=ScheduledEventType)
    """The type of the scheduled event"""
    start_time: Timestamp = attrs.field(repr=False, converter=timestamp_converter)
    """A Timestamp object representing the scheduled start time of the event """
    end_time: Optional[Timestamp] = attrs.field(repr=False, default=None, converter=optional(timestamp_converter))
    """Optional Timstamp object representing the scheduled end time, required if entity_type is EXTERNAL"""
    privacy_level: Union[ScheduledEventPrivacyLevel, int] = attrs.field(
        repr=False, converter=ScheduledEventPrivacyLevel
    )
    """
    Privacy level of the scheduled event

    ??? note
        Discord only has `GUILD_ONLY` at the momment.
    """
    status: Union[ScheduledEventStatus, int] = attrs.field(repr=False, converter=ScheduledEventStatus)
    """Current status of the scheduled event"""
    entity_id: Optional["Snowflake_Type"] = attrs.field(repr=False, default=MISSING, converter=optional(to_snowflake))
    """The id of an entity associated with a guild scheduled event"""
    entity_metadata: Optional[Dict[str, Any]] = attrs.field(repr=False, default=MISSING)  # TODO make this
    """The metadata associated with the entity_type"""
    user_count: Absent[int] = attrs.field(repr=False, default=MISSING)  # TODO make this optional and None in 6.0
    """Amount of users subscribed to the scheduled event"""
    cover: Asset | None = attrs.field(repr=False, default=None)
    """The cover image of this event"""

    _guild_id: "Snowflake_Type" = attrs.field(repr=False, converter=to_snowflake)
    _creator: Optional["User"] = attrs.field(repr=False, default=MISSING)
    _creator_id: Optional["Snowflake_Type"] = attrs.field(repr=False, default=MISSING, converter=optional(to_snowflake))
    _channel_id: Optional["Snowflake_Type"] = attrs.field(repr=False, default=None, converter=optional(to_snowflake))

    @property
    async def creator(self) -> Optional["User"]:
        """
        Returns the user who created this event.

        !!! note
            Events made before October 25th, 2021 will not have a creator.

        """
        return await self._client.cache.fetch_user(self._creator_id) if self._creator_id else None

    @property
    def guild(self) -> "Guild":
        return self._client.cache.get_guild(self._guild_id)

    @classmethod
    def _process_dict(cls, data: Dict[str, Any], client: "Client") -> Dict[str, Any]:
        if data.get("creator"):
            data["creator"] = client.cache.place_user_data(data["creator"])

        if data.get("channel_id"):
            data["channel"] = client.cache.get_channel(data["channel_id"])

        data["start_time"] = data.get("scheduled_start_time")

        if end_time := data.get("scheduled_end_time"):
            data["end_time"] = end_time
        else:
            data["end_time"] = None

        if image := data.get("image"):
            data["cover"] = Asset.from_path_hash(client, f"guild-events/{data['id']}/{{}}", image)

        data = super()._process_dict(data, client)
        return data

    @property
    def location(self) -> Optional[str]:
        """Returns the external locatian of this event."""
        if self.entity_type == ScheduledEventType.EXTERNAL:
            return self.entity_metadata["location"]
        return None

    async def fetch_channel(self, *, force: bool = False) -> Optional[Union["GuildVoice", "GuildStageVoice"]]:
        """
        Returns the channel this event is scheduled in if it is scheduled in a channel.

        Args:
            force: Whether to force fetch the channel from the API
        """
        if self._channel_id:
            return await self._client.cache.fetch_channel(self._channel_id, force=force)
        return None

    def get_channel(self) -> Optional[Union["GuildVoice", "GuildStageVoice"]]:
        """Returns the channel this event is scheduled in if it is scheduled in a channel."""
        if self._channel_id:
            return self._client.cache.get_channel(self._channel_id)
        return None

    async def fetch_event_users(
        self,
        limit: Optional[int] = 100,
        with_member_data: bool = False,
        before: Absent[Optional["Snowflake_Type"]] = MISSING,
        after: Absent[Optional["Snowflake_Type"]] = MISSING,
    ) -> List[Union["Member", "User"]]:
        """
        Fetch event users.

        Args:
            limit: Discord defualts to 100
            with_member_data: Whether to include guild member data
            before: Snowflake of a user to get before
            after: Snowflake of a user to get after

        !!! note
            This method is paginated

        """
        event_users = await self._client.http.get_scheduled_event_users(
            self._guild_id, self.id, limit, with_member_data, before, after
        )
        participants = []
        for u in event_users:
            if member := u.get("member"):
                u["member"]["user"] = u["user"]
                participants.append(self._client.cache.place_member_data(self._guild_id, member))
            else:
                participants.append(self._client.cache.place_user_data(u["user"]))

        return participants

    async def delete(self, reason: Absent[str] = MISSING) -> None:
        """
        Deletes this event.

        Args:
            reason: The reason for deleting this event

        """
        await self._client.http.delete_scheduled_event(self._guild_id, self.id, reason)

    async def edit(
        self,
        *,
        name: Absent[str] = MISSING,
        start_time: Absent["Timestamp"] = MISSING,
        end_time: Absent["Timestamp"] = MISSING,
        status: Absent[ScheduledEventStatus] = MISSING,
        description: Absent[str] = MISSING,
        channel_id: Absent[Optional["Snowflake_Type"]] = MISSING,
        event_type: Absent[ScheduledEventType] = MISSING,
        external_location: Absent[Optional[str]] = MISSING,
        entity_metadata: Absent[dict] = MISSING,
        privacy_level: Absent[ScheduledEventPrivacyLevel] = MISSING,
        cover_image: Absent[UPLOADABLE_TYPE] = MISSING,
        reason: Absent[str] = MISSING,
    ) -> None:
        """
        Edits this event.

        Args:
            name: The name of the event
            description: The description of the event
            channel_id: The channel id of the event
            event_type: The type of the event
            start_time: The scheduled start time of the event
            end_time: The scheduled end time of the event
            status: The status of the event
            external_location: The location of the event (1-100 characters)
            entity_metadata: The metadata of the event
            privacy_level: The privacy level of the event
            cover_image: the cover image of the scheduled event
            reason: The reason for editing the event

        !!! note
            If updating event_type to EXTERNAL:
                `channel_id` is required and must be set to null

                `external_location` or `entity_metadata` with a location field must be provided

                `end_time` must be provided

        """
        if external_location is not MISSING:
            entity_metadata = {"location": external_location}

        if event_type == ScheduledEventType.EXTERNAL:
            channel_id = None
            if external_location == MISSING:
                raise EventLocationNotProvided("Location is required for external events")

        payload = {
            "name": name,
            "description": description,
            "channel_id": channel_id,
            "entity_type": event_type,
            "scheduled_start_time": start_time.isoformat() if start_time else MISSING,
            "scheduled_end_time": end_time.isoformat() if end_time else MISSING,
            "status": status,
            "entity_metadata": entity_metadata,
            "privacy_level": privacy_level,
            "image": to_image_data(cover_image) if cover_image else MISSING,
        }
        await self._client.http.modify_scheduled_event(self._guild_id, self.id, payload, reason)
