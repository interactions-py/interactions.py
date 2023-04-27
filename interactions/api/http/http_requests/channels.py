from typing import TYPE_CHECKING, Optional, Sequence, cast, overload

import discord_typings

from interactions.models.internal.protocols import CanRequest
from interactions.models.discord.enums import (
    ChannelType,
    StagePrivacyLevel,
    Permissions,
    OverwriteType,
)
from interactions.client.utils.serializer import dict_filter_none

from ..route import Route, PAYLOAD_TYPE

__all__ = ("ChannelRequests",)


if TYPE_CHECKING:
    from interactions.models.discord.channel import PermissionOverwrite
    from interactions.models.discord.snowflake import Snowflake_Type


class ChannelRequests(CanRequest):
    async def get_channel(self, channel_id: "Snowflake_Type") -> discord_typings.ChannelData:
        """
        Get a channel by ID. Returns a channel object. If the channel is a thread, a thread member object is included.

        Args:
            channel_id: The id of the channel

        Returns:
            channel

        """
        result = await self.request(Route("GET", "/channels/{channel_id}", channel_id=channel_id))
        return cast(discord_typings.ChannelData, result)

    @overload
    async def get_channel_messages(
        self,
        channel_id: "Snowflake_Type",
        limit: int = 50,
    ) -> list[discord_typings.MessageData]:
        ...

    @overload
    async def get_channel_messages(
        self,
        channel_id: "Snowflake_Type",
        limit: int = 50,
        *,
        around: "Snowflake_Type | None" = None,
    ) -> list[discord_typings.MessageData]:
        ...

    @overload
    async def get_channel_messages(
        self,
        channel_id: "Snowflake_Type",
        limit: int = 50,
        *,
        before: "Snowflake_Type | None" = None,
    ) -> list[discord_typings.MessageData]:
        ...

    @overload
    async def get_channel_messages(
        self,
        channel_id: "Snowflake_Type",
        limit: int = 50,
        *,
        after: "Snowflake_Type | None" = None,
    ) -> list[discord_typings.MessageData]:
        ...

    async def get_channel_messages(
        self,
        channel_id: "Snowflake_Type",
        limit: int = 50,
        *,
        around: "Snowflake_Type | None" = None,
        before: "Snowflake_Type | None" = None,
        after: "Snowflake_Type | None" = None,
    ) -> list[discord_typings.MessageData]:
        """
        Get the messages for a channel.

        Args:
            channel_id: The channel to get messages from
            limit: How many messages to get (default 50, max 100)
            around: Get messages around this snowflake
            before: Get messages before this snowflake
            after: Get messages after this snowflake

        Returns:
            List of message dicts

        """
        params_count = sum(bool(param) for param in (before, after, around))
        if params_count > 1:
            raise ValueError("`before` `after` and `around` are mutually exclusive, only one may be passed at a time.")

        params: PAYLOAD_TYPE = {
            "limit": limit,
            "before": int(before) if before else None,
            "after": int(after) if after else None,
            "around": int(around) if around else None,
        }
        params = dict_filter_none(params)

        result = await self.request(
            Route("GET", "/channels/{channel_id}/messages", channel_id=channel_id), params=params
        )
        return cast(list[discord_typings.MessageData], result)

    async def create_guild_channel(
        self,
        guild_id: "Snowflake_Type",
        name: str,
        channel_type: "ChannelType | int",
        topic: str | None = None,
        position: int | None = None,
        permission_overwrites: Sequence["PermissionOverwrite | dict"] | None = None,
        parent_id: "Snowflake_Type | None" = None,
        nsfw: bool = False,
        bitrate: int = 64000,
        user_limit: int = 0,
        rate_limit_per_user: int = 0,
        reason: str | None = None,
        **kwargs: dict,
    ) -> discord_typings.ChannelData:
        """
        Create a channel in a guild.

        Args:
            guild_id: The ID of the guild to create the channel in
            name: The name of the channel
            channel_type: The type of channel to create
            topic: The topic of the channel
            position: The position of the channel in the channel list
            permission_overwrites: Permission overwrites to apply to the channel
            parent_id: The category this channel should be within
            nsfw: Should this channel be marked nsfw
            bitrate: The bitrate of this channel, only for voice
            user_limit: The max users that can be in this channel, only for voice
            rate_limit_per_user: The time users must wait between sending messages
            reason: The reason for creating this channel
            kwargs: Additional keyword arguments to pass to the request

        Returns:
            The created channel object

        """
        payload: PAYLOAD_TYPE = {
            "name": name,
            "type": channel_type,
            "topic": topic,
            "position": position,
            "rate_limit_per_user": rate_limit_per_user,
            "nsfw": nsfw,
            "parent_id": int(parent_id) if parent_id else None,
            "permission_overwrites": list(permission_overwrites) if permission_overwrites else None,
            **kwargs,
        }
        if channel_type in (ChannelType.GUILD_VOICE, ChannelType.GUILD_STAGE_VOICE):
            payload.update(
                bitrate=bitrate,
                user_limit=user_limit,
            )
        payload = dict_filter_none(payload)

        result = await self.request(
            Route("POST", "/guilds/{guild_id}/channels", guild_id=guild_id), payload=payload, reason=reason
        )
        return cast(discord_typings.ChannelData, result)

    async def move_channel(
        self,
        guild_id: "Snowflake_Type",
        channel_id: "Snowflake_Type",
        new_pos: int,
        parent_id: "Snowflake_Type | None" = None,
        lock_perms: bool = False,
        reason: str | None = None,
    ) -> None:
        """
        Move a channel.

        Args:
            guild_id: The ID of the guild this affects
            channel_id: The ID of the channel to move
            new_pos: The new position of this channel
            parent_id: The parent ID if needed
            lock_perms: Sync permissions with the new parent
            reason: An optional reason for the audit log

        """
        payload: PAYLOAD_TYPE = {
            "id": int(channel_id),
            "position": new_pos,
            "parent_id": int(parent_id) if parent_id else None,
            "lock_permissions": lock_perms,
        }
        payload = dict_filter_none(payload)

        await self.request(
            Route("PATCH", "/guilds/{guild_id}/channels", guild_id=guild_id), payload=payload, reason=reason
        )

    async def modify_channel(
        self, channel_id: "Snowflake_Type", data: dict, reason: str | None = None
    ) -> discord_typings.ChannelData:
        """
        Update a channel's settings, returns the updated channel object on success.

        Args:
            channel_id: The ID of the channel to update
            data: The data to update with
            reason: An optional reason for the audit log

        Returns:
            Channel object on success

        """
        result = await self.request(
            Route("PATCH", "/channels/{channel_id}", channel_id=channel_id), payload=data, reason=reason
        )
        return cast(discord_typings.ChannelData, result)

    async def delete_channel(self, channel_id: "Snowflake_Type", reason: str | None = None) -> None:
        """
        Delete the channel.

        Args:
            channel_id: The ID of the channel to delete
            reason: An optional reason for the audit log

        """
        await self.request(Route("DELETE", "/channels/{channel_id}", channel_id=channel_id), reason=reason)

    async def get_channel_invites(self, channel_id: "Snowflake_Type") -> list[discord_typings.InviteData]:
        """
        Get the invites for the channel.

        Args:
            channel_id: The ID of the channel to retrieve from

        Returns:
            List of invite objects

        """
        result = await self.request(Route("GET", "/channels/{channel_id}/invites", channel_id=channel_id))
        return cast(list[discord_typings.InviteData], result)

    @overload
    async def create_channel_invite(
        self,
        channel_id: "Snowflake_Type",
        max_age: int = 86400,
        max_uses: int = 0,
        temporary: bool = False,
        unique: bool = False,
        *,
        reason: str | None = None,
    ) -> discord_typings.InviteData:
        ...

    @overload
    async def create_channel_invite(
        self,
        channel_id: "Snowflake_Type",
        max_age: int = 86400,
        max_uses: int = 0,
        temporary: bool = False,
        unique: bool = False,
        *,
        target_user_id: "Snowflake_Type | None" = None,
        reason: str | None = None,
    ) -> discord_typings.InviteData:
        ...

    @overload
    async def create_channel_invite(
        self,
        channel_id: "Snowflake_Type",
        max_age: int = 86400,
        max_uses: int = 0,
        temporary: bool = False,
        unique: bool = False,
        *,
        target_application_id: "Snowflake_Type | None" = None,
        reason: str | None = None,
    ) -> discord_typings.InviteData:
        ...

    async def create_channel_invite(
        self,
        channel_id: "Snowflake_Type",
        max_age: int = 86400,
        max_uses: int = 0,
        temporary: bool = False,
        unique: bool = False,
        *,
        target_user_id: "Snowflake_Type | None" = None,
        target_application_id: "Snowflake_Type | None" = None,
        reason: str | None = None,
    ) -> discord_typings.InviteData:
        """
        Create an invite for the given channel.

        Args:
            channel_id: The ID of the channel to create an invite for
            max_age: duration of invite in seconds before expiry, or 0 for never. between 0 and 604800 (7 days) (default 24 hours)
            max_uses: max number of uses or 0 for unlimited. between 0 and 100
            temporary: whether this invite only grants temporary membership
            unique: if true, don't try to reuse a similar invite (useful for creating many unique one time use invites)
            target_user_id: the id of the user whose stream to display for this invite, the user must be streaming in the channel
            target_application_id: the id of the embedded application to open for this invite, the application must have the EMBEDDED flag
            reason: An optional reason for the audit log

        Returns:
            an invite object

        """
        params_count = sum(bool(param) for param in (target_user_id, target_application_id))
        if params_count > 1:
            raise ValueError(
                "`target_type` and `target_user_id` are mutually exclusive, only one may be passed at a time."
            )

        payload: PAYLOAD_TYPE = {
            "max_age": max_age,
            "max_uses": max_uses,
            "temporary": temporary,
            "unique": unique,
        }
        if target_user_id:
            payload["target_type"] = 1
            payload["target_user_id"] = int(target_user_id)
        if target_application_id:
            payload["target_type"] = 2
            payload["target_application_id"] = int(target_application_id)
        payload = dict_filter_none(payload)

        result = await self.request(
            Route("POST", "/channels/{channel_id}/invites", channel_id=channel_id), payload=payload, reason=reason
        )
        return cast(discord_typings.InviteData, result)

    async def get_invite(
        self,
        invite_code: str,
        with_counts: bool = False,
        with_expiration: bool = True,
        scheduled_event_id: "Snowflake_Type | None" = None,
    ) -> discord_typings.InviteData:
        """
        Get an invite object for a given code.

        Args:
            invite_code: The code of the invite
            with_counts: whether the invite should contain approximate member counts
            with_expiration: whether the invite should contain the expiration date
            scheduled_event_id: the guild scheduled event to include with the invite

        Returns:
            an invite object

        """
        params: PAYLOAD_TYPE = {
            "invite_code": invite_code,
            "with_counts": with_counts,
            "with_expiration": with_expiration,
            "guild_scheduled_event_id": int(scheduled_event_id) if scheduled_event_id else None,
        }
        params = dict_filter_none(params)

        result = await self.request(Route("GET", "/invites/{invite_code}", invite_code=invite_code, params=params))
        return cast(discord_typings.InviteData, result)

    async def delete_invite(self, invite_code: str, reason: str | None = None) -> discord_typings.InviteData:
        """
        Delete an invite.

        Args:
            invite_code: The code of the invite to delete
            reason: The reason to delete the invite

        Returns:
            The deleted invite object

        """
        result = await self.request(Route("DELETE", "/invites/{invite_code}", invite_code=invite_code), reason=reason)
        return cast(discord_typings.InviteData, result)

    async def edit_channel_permission(
        self,
        channel_id: "Snowflake_Type",
        overwrite_id: "Snowflake_Type",
        perm_type: "OverwriteType | int",
        allow: "Permissions | int" = 0,
        deny: "Permissions | int" = 0,
        reason: str | None = None,
    ) -> None:
        """
        Edit the channel permission overwrites for a user or role in a channel.

        Args:
            channel_id: The id of the channel
            overwrite_id: The id of the object to override
            allow: the bitwise value of all allowed permissions
            deny: the bitwise value of all disallowed permissions
            perm_type: 0 for a role or 1 for a member
            reason: The reason for this action

        """
        payload: PAYLOAD_TYPE = {"allow": allow, "deny": deny, "type": perm_type}

        await self.request(
            Route(
                "PUT",
                "/channels/{channel_id}/permissions/{overwrite_id}",
                channel_id=channel_id,
                overwrite_id=overwrite_id,
            ),
            payload=payload,
            reason=reason,
        )

    async def delete_channel_permission(
        self,
        channel_id: "Snowflake_Type",
        overwrite_id: "Snowflake_Type",
        reason: str | None = None,
    ) -> None:
        """
        Delete a channel permission overwrite for a user or role in a channel.

        Args:
            channel_id: The ID of the channel.
            overwrite_id: The ID of the overwrite
            reason: An optional reason for the audit log

        """
        await self.request(
            Route("DELETE", "/channels/{channel_id}/{overwrite_id}", channel_id=channel_id, overwrite_id=overwrite_id),
            reason=reason,
        )

    async def follow_news_channel(
        self, channel_id: "Snowflake_Type", webhook_channel_id: "Snowflake_Type"
    ) -> discord_typings.FollowedChannelData:
        """
        Follow a news channel to send messages to the target channel.

        Args:
            channel_id: The channel to follow
            webhook_channel_id: ID of the target channel

        Returns:
            Followed channel object

        """
        payload = {"webhook_channel_id": int(webhook_channel_id)}

        result = await self.request(
            Route("POST", "/channels/{channel_id}/followers", channel_id=channel_id), payload=payload
        )
        return cast(discord_typings.FollowedChannelData, result)

    async def trigger_typing_indicator(self, channel_id: "Snowflake_Type") -> None:
        """
        Post a typing indicator for the specified channel. Generally bots should not implement this route.

        Args:
            channel_id: The id of the channel to "type" in

        """
        await self.request(Route("POST", "/channels/{channel_id}/typing", channel_id=channel_id))

    async def get_pinned_messages(self, channel_id: "Snowflake_Type") -> list[discord_typings.MessageData]:
        """
        Get all pinned messages from a channel.

        Args:
            channel_id: The ID of the channel to get pins from

        Returns:
            A list of pinned message objects

        """
        result = await self.request(Route("GET", "/channels/{channel_id}/pins", channel_id=channel_id))
        return cast(list[discord_typings.MessageData], result)

    async def create_stage_instance(
        self,
        channel_id: "Snowflake_Type",
        topic: str,
        privacy_level: StagePrivacyLevel | int = StagePrivacyLevel.PUBLIC,
        reason: str | None = None,
    ) -> discord_typings.StageInstanceData:
        """
        Create a new stage instance.

        Args:
            channel_id: The ID of the stage channel
            topic: The topic of the stage instance (1-120 characters)
            privacy_level: Them privacy_level of the stage instance (default guild only)
            reason: The reason for the creating the stage instance

        Returns:
            The stage instance

        """
        payload: PAYLOAD_TYPE = {
            "channel_id": int(channel_id),
            "topic": topic,
            "privacy_level": StagePrivacyLevel(privacy_level),
        }

        result = await self.request(Route("POST", "/stage-instances"), payload=payload, reason=reason)
        return cast(discord_typings.StageInstanceData, result)

    async def get_stage_instance(self, channel_id: "Snowflake_Type") -> discord_typings.StageInstanceData:
        """
        Get the stage instance associated with a given channel, if it exists.

        Args:
            channel_id: The ID of the channel to retrieve the instance for.

        Returns:
            A stage instance.

        """
        result = await self.request(Route("GET", "/stage-instances/{channel_id}", channel_id=channel_id))
        return cast(discord_typings.StageInstanceData, result)

    async def modify_stage_instance(
        self,
        channel_id: "Snowflake_Type",
        topic: str | None = None,
        privacy_level: int | None = None,
        reason: str | None = None,
    ) -> discord_typings.StageInstanceData:
        """
        Update the fields of a given stage instance.

        Args:
            channel_id: The id of the stage channel.
            topic: The new topic for the stage instance
            privacy_level: The privacy level for the stage instance
            reason: The reason for the change

        Returns:
            The updated stage instance.

        """
        payload: PAYLOAD_TYPE = {"topic": topic, "privacy_level": privacy_level}
        payload = dict_filter_none(payload)
        result = await self.request(
            Route("PATCH", "/stage-instances/{channel_id}", channel_id=channel_id), payload=payload, reason=reason
        )
        return cast(discord_typings.StageInstanceData, result)

    async def delete_stage_instance(self, channel_id: "Snowflake_Type", reason: str | None = None) -> None:
        """
        Delete a stage instance.

        Args:
            channel_id: The ID of the channel to delete the stage instance for.
            reason: The reason for the deletion

        """
        await self.request(Route("DELETE", "/stage-instances/{channel_id}", channel_id=channel_id), reason=reason)

    async def create_tag(
        self,
        channel_id: "Snowflake_Type",
        name: str,
        emoji_id: Optional["Snowflake_Type"] = None,
        emoji_name: Optional[str] = None,
    ) -> discord_typings.ChannelData:
        """
        Create a new tag.

        Args:
            channel_id: The ID of the forum channel to create tag for.
            name: The name of the tag
            emoji_id: The ID of the emoji to use for the tag
            emoji_name: The name of the emoji to use for the tag

        !!! note
            Can either have an `emoji_id` or an `emoji_name`, but not both.
            `emoji_id` is meant for custom emojis, `emoji_name` is meant for unicode emojis.
        """
        payload: PAYLOAD_TYPE = {
            "name": name,
            "emoji_id": int(emoji_id) if emoji_id else None,
            "emoji_name": emoji_name or None,
        }
        payload = dict_filter_none(payload)

        result = await self.request(
            Route("POST", "/channels/{channel_id}/tags", channel_id=channel_id), payload=payload
        )
        return cast(discord_typings.ChannelData, result)

    async def edit_tag(
        self,
        channel_id: "Snowflake_Type",
        tag_id: "Snowflake_Type",
        name: str,
        emoji_id: "Snowflake_Type | None" = None,
        emoji_name: str | None = None,
    ) -> discord_typings.ChannelData:
        """
        Update a tag.

        Args:
            channel_id: The ID of the forum channel to edit tag it.
            tag_id: The ID of the tag to update
            name: The new name of the tag
            emoji_id: The ID of the emoji to use for the tag
            emoji_name: The name of the emoji to use for the tag

        !!! note
            Can either have an `emoji_id` or an `emoji_name`, but not both.
            emoji`_id is meant for custom emojis, `emoji_name` is meant for unicode emojis.
        """
        payload: PAYLOAD_TYPE = {
            "name": name,
            "emoji_id": int(emoji_id) if emoji_id else None,
            "emoji_name": emoji_name,
        }
        payload = dict_filter_none(payload)

        result = await self.request(
            Route("PUT", "/channels/{channel_id}/tags/{tag_id}", channel_id=channel_id, tag_id=tag_id), payload=payload
        )
        return cast(discord_typings.ChannelData, result)

    async def delete_tag(self, channel_id: "Snowflake_Type", tag_id: "Snowflake_Type") -> discord_typings.ChannelData:
        """
        Delete a forum tag.

        Args:
            channel_id: The ID of the forum channel to delete tag it.
            tag_id: The ID of the tag to delete
        """
        result = await self.request(
            Route("DELETE", "/channels/{channel_id}/tags/{tag_id}", channel_id=channel_id, tag_id=tag_id)
        )
        return cast(discord_typings.ChannelData, result)
