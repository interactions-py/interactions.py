from typing import Dict, List, Optional, Union

from ...api.cache import Cache
from ..error import LibraryException
from ..models.channel import Channel
from ..models.message import Message
from ..models.misc import Snowflake
from .request import _Request
from .route import Route

__all__ = ("ChannelRequest",)


class ChannelRequest:
    _req: _Request
    cache: Cache

    def __init__(self) -> None:
        pass

    async def get_channel(self, channel_id: int) -> dict:
        """
        Gets a channel by ID. If the channel is a thread, it also includes thread members (and other thread attributes).

        :param channel_id: Channel ID snowflake.
        :return: Dictionary of the channel object.
        """
        request = await self._req.request(Route("GET", f"/channels/{channel_id}"))
        self.cache[Channel].merge(Channel(**request, _client=self))

        return request

    async def delete_channel(self, channel_id: int) -> None:
        """
        Deletes a channel.

        :param channel_id: Channel ID snowflake
        """
        return await self._req.request(
            Route("DELETE", "/channels/{channel_id}", channel_id=channel_id)
        )

    async def get_channel_messages(
        self,
        channel_id: int,
        limit: int = 50,
        around: Optional[int] = None,
        before: Optional[int] = None,
        after: Optional[int] = None,
    ) -> List[dict]:
        """
        Get messages from a channel.

        .. note::
            around, before, and after arguments are mutually exclusive.

        :param channel_id: Channel ID snowflake.
        :param limit: How many messages to get. Defaults to 50, the max is 100.
        :param around: Get messages around this snowflake ID.
        :param before: Get messages before this snowflake ID.
        :param after: Get messages after this snowflake ID.
        :return: An array of Message objects.
        """
        params: Dict[str, Union[int, str]] = {"limit": limit}

        params_used = 0

        if before:
            params_used += 1
            params["before"] = before
        if after:
            params_used += 1
            params["after"] = after
        if around:
            params_used += 1
            params["around"] = around

        if params_used > 1:
            raise LibraryException(
                message="`before`, `after` and `around` are mutually exclusive. Please pass only one of them.",
                code=12,
            )

        request = await self._req.request(
            Route("GET", f"/channels/{channel_id}/messages"), params=params
        )

        if isinstance(request, list):
            for message in request:
                if message.get("id"):
                    self.cache[Message].merge(Message(**message, _client=self))

        return request

    async def create_channel(
        self, guild_id: int, payload: dict, reason: Optional[str] = None
    ) -> dict:
        """
        Creates a channel within a guild.

        .. note::
            This does not handle payload in this method. Tread carefully.

        :param guild_id: Guild ID snowflake.
        :param payload: Payload data.
        :param reason: Reason to show in audit log, if needed.
        :return: Channel object as dictionary.
        """
        request = await self._req.request(
            Route("POST", f"/guilds/{guild_id}/channels"), json=payload, reason=reason
        )

        return request

    async def move_channel(
        self,
        guild_id: int,
        channel_id: int,
        new_pos: int,
        parent_id: Optional[int],
        lock_perms: bool = False,
        reason: Optional[str] = None,
    ) -> dict:
        """
        Moves a channel to a new position.

        :param guild_id: Guild ID snowflake.
        :param channel_id: Channel ID snowflake.
        :param new_pos: The new channel position.
        :param parent_id: The category parent ID, if needed.
        :param lock_perms: Sync permissions with the parent associated with parent_id. Defaults to False.
        :param reason: Reason to display to the audit log, if any.
        :return: ?
        """
        payload = {"id": channel_id, "position": new_pos, "lock_permissions": lock_perms}
        if parent_id:
            payload["parent_id"] = parent_id

        return await self._req.request(
            Route("PATCH", f"/guilds/{guild_id}/channels"), json=payload, reason=reason
        )

    async def modify_channel(
        self, channel_id: int, payload: dict, reason: Optional[str] = None
    ) -> dict:
        """
        Update a channel's settings.

        :param channel_id: Channel ID snowflake.
        :param payload: Data representing updated settings.
        :param reason: Reason, if any.
        :return: Channel with updated attributes, if successful.
        """
        return await self._req.request(
            Route("PATCH", f"/channels/{channel_id}"), json=payload, reason=reason
        )

    async def get_channel_invites(self, channel_id: int) -> List[dict]:
        """
        Get the invites for the channel.

        :param channel_id: Channel ID snowflake.
        :return: List of invite objects
        """
        return await self._req.request(Route("GET", f"/channels/{channel_id}/invites"))

    async def create_channel_invite(
        self, channel_id: int, payload: dict, reason: Optional[str] = None
    ) -> dict:
        """
        Creates an invite for the given channel.

        .. note::
            This method does not handle payload. It just sends it.

        :param channel_id: Channel ID snowflake.
        :param payload: Data representing the payload/invite attributes.
        :param reason: Reason to show in the audit log, if any.
        :return: An invite object.
        """
        return await self._req.request(
            Route("POST", f"/channels/{channel_id}/invites"), json=payload, reason=reason
        )

    async def edit_channel_permission(
        self,
        channel_id: int,
        overwrite_id: int,
        allow: str,
        deny: str,
        perm_type: int,
        reason: Optional[str] = None,
    ) -> None:
        """
        Edits the channel's permission overwrites for a user or role in a given channel.

        :param channel_id: Channel ID snowflake.
        :param overwrite_id: The ID of the overridden object.
        :param allow: the bitwise value of all allowed permissions
        :param deny: the bitwise value of all disallowed permissions
        :param perm_type: 0 for a role or 1 for a member
        :param reason: Reason to display in the Audit Log, if given.
        """
        return await self._req.request(
            Route("PUT", f"/channels/{channel_id}/permissions/{overwrite_id}"),
            json={"allow": allow, "deny": deny, "type": perm_type},
            reason=reason,
        )

    async def delete_channel_permission(
        self, channel_id: int, overwrite_id: int, reason: Optional[str] = None
    ) -> None:
        """
        Deletes a channel permission overwrite for a user or role in a channel.

        :param channel_id: Channel ID snowflake.
        :param overwrite_id: The ID of the overridden object.
        :param reason: Reason to display in the Audit Log, if given.
        """
        return await self._req.request(
            Route("DELETE", f"/channels/{channel_id}/{overwrite_id}"), reason=reason
        )

    async def trigger_typing(self, channel_id: int) -> None:
        """
        Posts "... is typing" in a given channel.

        .. note::
            By default, this lib doesn't use this endpoint, however, this is listed for third-party implementation.

        :param channel_id: Channel ID snowflake.
        """
        return await self._req.request(Route("POST", f"/channels/{channel_id}/typing"))

    async def get_pinned_messages(self, channel_id: int) -> List[dict]:
        """
        Get all pinned messages from a channel.

        :param channel_id: Channel ID snowflake.
        :return: A list of pinned message objects.
        """
        return await self._req.request(Route("GET", f"/channels/{channel_id}/pins"))

    async def create_stage_instance(
        self, channel_id: int, topic: str, privacy_level: int = 1, reason: Optional[str] = None
    ) -> dict:
        """
        Create a new stage instance.

        :param channel_id: Channel ID snowflake.
        :param topic: The topic of the stage instance. Limited to 1-120 characters.
        :param privacy_level: The privacy_level of the stage instance (defaults to guild-only "1").
        :param reason: The reason for the creating the stage instance, if any.
        :return: The new stage instance
        """
        return await self._req.request(
            Route("POST", "/stage-instances"),
            json={
                "channel_id": channel_id,
                "topic": topic,
                "privacy_level": privacy_level,
            },
            reason=reason,
        )

    async def get_stage_instance(self, channel_id: int) -> dict:
        """
        Get the stage instance associated with a given channel, if it exists.

        :param channel_id: Channel ID snowflake.
        :return: A stage instance.
        """
        return await self._req.request(Route("GET", f"/stage-instances/{channel_id}"))

    async def modify_stage_instance(
        self,
        channel_id: int,
        topic: Optional[str] = None,
        privacy_level: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> dict:
        """
        Update the fields of a given stage instance.

        :param channel_id: Channel ID snowflake.
        :param topic: The new topic of the stage instance, if given. Limited to 1-120 characters.
        :param privacy_level: The new privacy_level of the stage instance.
        :param reason: The reason for the creating the stage instance, if any.
        :return: The updated stage instance.
        """
        return await self._req.request(
            Route("PATCH", f"/stage-instances/{channel_id}"),
            json={
                k: v
                for k, v in {"topic": topic, "privacy_level": privacy_level}.items()
                if v is not None
            },
            reason=reason,
        )

    async def delete_stage_instance(self, channel_id: int, reason: Optional[str] = None) -> None:
        """
        Delete a stage instance.

        :param channel_id: Channel ID snowflake.
        :param reason: The reason for the creating the stage instance, if any.
        """
        return await self._req.request(
            Route("DELETE", f"/stage-instances/{channel_id}"), reason=reason
        )

    async def create_tag(
        self,
        channel_id: int,
        name: str,
        moderated: bool = False,
        emoji_id: Optional[int] = None,
        emoji_name: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> dict:
        """
        Create a new tag.

        .. note::
            Can either have an emoji_id or an emoji_name, but not both.
            emoji_id is meant for custom emojis, emoji_name is meant for unicode emojis.

        :param channel_id: Channel ID snowflake.
        :param name: The name of the tag
        :param moderated: Whether the tag can only be assigned to moderators or not. Defaults to ``False``
        :param emoji_id: The ID of the emoji to use for the tag
        :param emoji_name: The name of the emoji to use for the tag
        :param reason: The reason for the creating the tag, if any.
        :return: A Forum tag.
        """

        # This *assumes* cache is up-to-date.

        _channel = self.cache[Channel].get(Snowflake(channel_id))
        _tags = [_._json for _ in _channel.available_tags]  # list of tags in dict form

        _dct = {"name": name, "moderated": moderated}
        if emoji_id:
            _dct["emoji_id"] = emoji_id
        if emoji_name:
            _dct["emoji_name"] = emoji_name

        _tags.append(_dct)

        updated_channel = await self.modify_channel(
            channel_id, {"available_tags": _tags}, reason=reason
        )
        _channel_obj = Channel(**updated_channel, _client=self)
        return _channel_obj.available_tags[-1]._json

    async def edit_tag(
        self,
        channel_id: int,
        tag_id: int,
        name: str,
        moderated: Optional[bool] = None,
        emoji_id: Optional[int] = None,
        emoji_name: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> dict:
        """
        Update a tag.

        .. note::
            Can either have an emoji_id or an emoji_name, but not both.
            emoji_id is meant for custom emojis, emoji_name is meant for unicode emojis.

            The object returns *will* have a different tag ID.

        :param channel_id: Channel ID snowflake.
        :param tag_id: The ID of the tag to update.
        :param moderated: Whether the tag can only be assigned to moderators or not. Defaults to ``False``
        :param name: The new name of the tag
        :param emoji_id: The ID of the emoji to use for the tag
        :param emoji_name: The name of the emoji to use for the tag
        :param reason: The reason for deleting the tag, if any.

        :return The updated tag object.
        """

        # This *assumes* cache is up-to-date.

        _channel = self.cache[Channel].get(Snowflake(channel_id))
        _tags = [_._json for _ in _channel.available_tags]  # list of tags in dict form

        _old_tag = [tag for tag in _tags if tag["id"] == tag_id][0]

        _tags.remove(_old_tag)

        _dct = {"name": name, "tag_id": tag_id}
        if moderated:
            _dct["moderated"] = moderated
        if emoji_id:
            _dct["emoji_id"] = emoji_id
        if emoji_name:
            _dct["emoji_name"] = emoji_name

        _tags.append(_dct)

        updated_channel = await self.modify_channel(
            channel_id, {"available_tags": _tags}, reason=reason
        )
        _channel_obj = Channel(**updated_channel, _client=self)

        self.cache[Channel].merge(_channel_obj)

        return [tag for tag in _channel_obj.available_tags if tag.name == name][0]

    async def delete_tag(self, channel_id: int, tag_id: int, reason: Optional[str] = None) -> None:
        """
        Delete a forum tag.

        :param channel_id: Channel ID snowflake.
        :param tag_id: The ID of the tag to delete
        :param reason: The reason for deleting the tag, if any.
        """
        _channel = self.cache[Channel].get(Snowflake(channel_id))
        _tags = [_._json for _ in _channel.available_tags]

        _old_tag = [tag for tag in _tags if tag["id"] == Snowflake(tag_id)][0]

        _tags.remove(_old_tag)

        request = await self.modify_channel(channel_id, {"available_tags": _tags}, reason=reason)

        self.cache[Channel].merge(Channel(**request, _client=self))
