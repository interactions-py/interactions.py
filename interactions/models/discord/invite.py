from typing import TYPE_CHECKING, Optional, Union, Dict, Any

import attrs

from interactions.client.const import MISSING, Absent
from interactions.client.utils.attr_converters import optional as optional_c
from interactions.client.utils.attr_converters import timestamp_converter
from interactions.models.discord.application import Application
from interactions.models.discord.enums import InviteTargetType
from interactions.models.discord.guild import GuildPreview
from interactions.models.discord.snowflake import to_snowflake
from interactions.models.discord.stage_instance import StageInstance
from interactions.models.discord.timestamp import Timestamp
from .base import ClientObject

if TYPE_CHECKING:
    from interactions.client import Client
    from interactions.models import TYPE_GUILD_CHANNEL, Guild
    from interactions.models.discord.user import User
    from interactions.models.discord.snowflake import Snowflake_Type

__all__ = ("Invite",)


@attrs.define(eq=False, order=False, hash=False, kw_only=True)
class Invite(ClientObject):
    code: str = attrs.field(repr=True)
    """The invite code (unique ID)"""

    # metadata
    uses: int = attrs.field(default=0, repr=True)
    """How many times this invite has been used"""
    max_uses: int = attrs.field(repr=False, default=0)
    """Max number of times this invite can be used"""
    max_age: int = attrs.field(repr=False, default=0)
    """Duration (in seconds) after which the invite expires"""
    created_at: Timestamp = attrs.field(default=MISSING, converter=optional_c(timestamp_converter), repr=True)
    """When this invite was created"""
    temporary: bool = attrs.field(default=False, repr=True)
    """Whether this invite only grants temporary membership"""

    # target data
    target_type: Optional[Union[InviteTargetType, int]] = attrs.field(
        default=None, converter=optional_c(InviteTargetType), repr=True
    )
    """The type of target for this voice channel invite"""
    approximate_presence_count: Optional[int] = attrs.field(repr=False, default=MISSING)
    """Approximate count of online members, returned when fetching invites with `with_counts` set as `True`"""
    approximate_member_count: Optional[int] = attrs.field(repr=False, default=MISSING)
    """Approximate count of total members, returned when fetching invites with `with_counts` set as `True`"""
    scheduled_event: Optional["Snowflake_Type"] = attrs.field(
        default=None, converter=optional_c(to_snowflake), repr=True
    )
    """Guild scheduled event data, only included if `guild_scheduled_event_id` contains a valid guild scheduled event id"""
    expires_at: Optional[Timestamp] = attrs.field(default=None, converter=optional_c(timestamp_converter), repr=True)
    """The expiration date of this invite, returned when fetching invites with `with_expiration` set as `True`"""
    stage_instance: Optional[StageInstance] = attrs.field(repr=False, default=None)
    """Stage instance data if there is a public Stage instance in the Stage channel this invite is for (deprecated)"""
    target_application: Optional[dict] = attrs.field(repr=False, default=None)
    """The embedded application to open for this voice channel embedded application invite"""
    guild_preview: Optional[GuildPreview] = attrs.field(repr=False, default=MISSING)
    """The guild this invite is for - not given in invite events"""

    # internal for props
    _channel_id: "Snowflake_Type" = attrs.field(converter=to_snowflake, repr=True)
    _guild_id: Optional["Snowflake_Type"] = attrs.field(default=None, converter=optional_c(to_snowflake), repr=True)
    _inviter_id: Optional["Snowflake_Type"] = attrs.field(default=None, converter=optional_c(to_snowflake), repr=True)
    _target_user_id: Optional["Snowflake_Type"] = attrs.field(
        repr=False, default=None, converter=optional_c(to_snowflake)
    )

    @property
    def channel(self) -> Optional["TYPE_GUILD_CHANNEL"]:
        """The cached channel the invite is for."""
        return self._client.cache.get_channel(self._channel_id)

    @property
    def guild(self) -> Optional["Guild"]:
        """The cached guild the invite is."""
        return self._client.cache.get_guild(self._guild_id) if self._guild_id else None

    @property
    def inviter(self) -> Optional["User"]:
        """The user that created the invite or None."""
        return self._client.cache.get_user(self._inviter_id) if self._inviter_id else None

    @property
    def target_user(self) -> Optional["User"]:
        """The user whose stream to display for this voice channel stream invite or None."""
        return self._client.cache.get_user(self._target_user_id) if self._target_user_id else None

    @classmethod
    def _process_dict(cls, data: Dict[str, Any], client: "Client") -> Dict[str, Any]:
        if "stage_instance" in data:
            data["stage_instance"] = StageInstance.from_dict(data, client)

        if "target_application" in data:
            data["target_application"] = Application.from_dict(data, client)

        if "target_event_id" in data:
            data["scheduled_event"] = data["target_event_id"]

        if channel := data.pop("channel", None):
            client.cache.place_channel_data(channel)
            data["channel_id"] = channel["id"]

        if guild := data.pop("guild", None):
            data["guild_preview"] = GuildPreview.from_dict(guild, client)
            data["guild_id"] = guild["id"]
        elif guild_id := data.pop("guild_id", None):
            data["guild_id"] = guild_id

        if inviter := data.pop("inviter", None):
            inviter = client.cache.place_user_data(inviter)
            data["inviter_id"] = inviter.id

        if target_user := data.pop("target_user", None):
            target_user = client.cache.place_user_data(target_user)
            data["target_user_id"] = target_user.id

        return data

    def __str__(self) -> str:
        return self.link

    @property
    def link(self) -> str:
        """The invite link."""
        if self.scheduled_event:
            return f"https://discord.gg/{self.code}?event={self.scheduled_event}"
        return f"https://discord.gg/{self.code}"

    async def delete(self, reason: Absent[str] = MISSING) -> None:
        """
        Delete this invite.

        !!! note
            You must have the `manage_channels` permission on the channel this invite belongs to.

        !!! note
            With `manage_guild` permission, you can delete any invite across the guild.

        Args:
            reason: The reason for the deletion of invite.

        """
        await self._client.http.delete_invite(self.code, reason=reason)
