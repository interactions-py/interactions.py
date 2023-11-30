from contextlib import suppress
from logging import Logger
from typing import TYPE_CHECKING, List, Dict, Any, Optional, Union

import attrs
import discord_typings

from interactions.client.const import Absent, MISSING, get_logger
from interactions.client.errors import NotFound, Forbidden
from interactions.client.utils.cache import TTLCache, NullCache
from interactions.models import VoiceState
from interactions.models.discord.channel import BaseChannel, GuildChannel, ThreadChannel
from interactions.models.discord.emoji import CustomEmoji
from interactions.models.discord.guild import Guild
from interactions.models.discord.message import Message
from interactions.models.discord.role import Role
from interactions.models.discord.snowflake import to_snowflake, to_optional_snowflake
from interactions.models.discord.user import Member, User
from interactions.models.discord.scheduled_event import ScheduledEvent
from interactions.models.internal.active_voice_state import ActiveVoiceState

__all__ = ("GlobalCache", "create_cache")


if TYPE_CHECKING:
    from interactions.client import Client
    from interactions.models.discord.channel import DM, TYPE_ALL_CHANNEL
    from interactions.models.discord.snowflake import Snowflake_Type


def create_cache(
    ttl: Optional[int] = 60,
    hard_limit: Optional[int] = 250,
    soft_limit: Absent[Optional[int]] = MISSING,
) -> Union[dict, TTLCache, NullCache]:
    """
    Create a cache object based on the parameters passed.

    If `ttl` and `max_values` are set to None, the cache will just be a regular dict, with no culling.

    Args:
        ttl: The time to live of an object in the cache
        hard_limit: The hard limit of values allowed to be within the cache
        soft_limit: The amount of values allowed before objects expire due to ttl

    Returns:
        dict or TTLCache based on parameters passed

    """
    if ttl is None and hard_limit is None:
        return {}
    if ttl == 0 and hard_limit == 0 and soft_limit == 0:
        return NullCache()
    if not soft_limit:
        soft_limit = int(hard_limit / 4) if hard_limit else 50
    return TTLCache(
        hard_limit=hard_limit or float("inf"),
        soft_limit=soft_limit or 0,
        ttl=ttl or float("inf"),
    )


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class GlobalCache:
    _client: "Client" = attrs.field(
        repr=False,
    )

    # Non expiring discord objects cache
    user_cache: dict = attrs.field(repr=False, factory=dict)  # key: user_id
    member_cache: dict = attrs.field(repr=False, factory=dict)  # key: (guild_id, user_id)
    channel_cache: dict = attrs.field(repr=False, factory=dict)  # key: channel_id
    guild_cache: dict = attrs.field(repr=False, factory=dict)  # key: guild_id
    scheduled_events_cache: dict = attrs.field(repr=False, factory=dict)  # key: guild_scheduled_event_id

    # Expiring discord objects cache
    message_cache: TTLCache = attrs.field(repr=False, factory=TTLCache)  # key: (channel_id, message_id)
    role_cache: TTLCache = attrs.field(repr=False, factory=dict)  # key: role_id
    voice_state_cache: TTLCache = attrs.field(repr=False, factory=dict)  # key: user_id
    bot_voice_state_cache: dict = attrs.field(repr=False, factory=dict)  # key: guild_id

    enable_emoji_cache: bool = attrs.field(repr=False, default=False)
    """If the emoji cache should be enabled. Default: False"""
    emoji_cache: Optional[dict] = attrs.field(repr=False, default=None, init=False)  # key: emoji_id

    # Expiring id reference cache
    dm_channels: TTLCache = attrs.field(repr=False, factory=TTLCache)  # key: user_id
    user_guilds: TTLCache = attrs.field(repr=False, factory=dict)  # key: user_id; value: set[guild_id]

    logger: Logger = attrs.field(repr=False, init=False, factory=get_logger)

    def __attrs_post_init__(self) -> None:
        if not isinstance(self.message_cache, TTLCache):
            self.logger.warning(
                "Disabling cache limits for message_cache is not recommended! This can result in very high memory usage"
            )

        # enable emoji cache
        if self.enable_emoji_cache:
            self.emoji_cache = {}

    # region User cache

    async def fetch_user(self, user_id: "Snowflake_Type", *, force: bool = False) -> User:
        """
        Fetch a user by their ID.

        Args:
            user_id: The user's ID
            force: If the cache should be ignored, and the user should be fetched from the API

        Returns:
            User object if found

        """
        user_id = to_snowflake(user_id)

        user = self.user_cache.get(user_id)
        if (user is None or user._fetched is False) or force:
            data = await self._client.http.get_user(user_id)
            user = self.place_user_data(data)
            user._fetched = True  # the user object should set this to True, but we do it here just in case
        return user

    def get_user(self, user_id: Optional["Snowflake_Type"]) -> Optional[User]:
        """
        Get a user by their ID.

        Args:
            user_id: The user's ID

        Returns:
            User object if found
        """
        return self.user_cache.get(to_optional_snowflake(user_id))

    def place_user_data(self, data: discord_typings.UserData) -> User:
        """
        Take json data representing a User, process it, and cache it.

        Args:
            data: json representation of user

        Returns:
            The processed User data
        """
        user_id = to_snowflake(data["id"])

        user = self.user_cache.get(user_id)

        if user is None:
            user = User.from_dict(data, self._client)
            self.user_cache[user_id] = user
        else:
            user.update_from_dict(data)
        return user

    def delete_user(self, user_id: "Snowflake_Type") -> None:
        """
        Delete a user from the cache.

        Args:
            user_id: The user's ID
        """
        self.user_cache.pop(to_snowflake(user_id), None)

    # endregion User cache

    # region Member cache

    async def fetch_member(
        self, guild_id: "Snowflake_Type", user_id: "Snowflake_Type", *, force: bool = False
    ) -> Member:
        """
        Fetch a member by their guild and user IDs.

        Args:
            guild_id: The ID of the guild this user belongs to
            user_id: The ID of the user
            force: If the cache should be ignored, and the member should be fetched from the API

        Returns:
            Member object if found

        """
        guild_id = to_snowflake(guild_id)
        user_id = to_snowflake(user_id)
        member = self.member_cache.get((guild_id, user_id))
        if member is None or force:
            data = await self._client.http.get_member(guild_id, user_id)
            member = self.place_member_data(guild_id, data)
        return member

    def get_member(self, guild_id: Optional["Snowflake_Type"], user_id: Optional["Snowflake_Type"]) -> Optional[Member]:
        """
        Get a member by their guild and user IDs.

        Args:
            guild_id: The ID of the guild this user belongs to
            user_id: The ID of the user

        Returns:
            Member object if found
        """
        return self.member_cache.get((to_optional_snowflake(guild_id), to_optional_snowflake(user_id)))

    def place_member_data(self, guild_id: "Snowflake_Type", data: discord_typings.GuildMemberData) -> Member:
        """
        Take json data representing a User, process it, and cache it.

        Args:
            guild_id: The ID of the guild this member belongs to
            data: json representation of the member

        Returns:
            The processed member
        """
        guild_id = to_snowflake(guild_id)
        is_user = "member" in data
        user_id = to_snowflake(data["user"]["id"] if "user" in data else data["id"])

        member = self.member_cache.get((guild_id, user_id))
        if member is None:
            member_extra = {"guild_id": guild_id}
            member = data["member"] if is_user else data
            member.update(member_extra)

            member = Member.from_dict(data, self._client)
            self.member_cache[(guild_id, user_id)] = member
        else:
            member.update_from_dict(data)

        self.place_user_guild(user_id, guild_id)
        if guild := self.guild_cache.get(guild_id):
            # todo: this is slow, find a faster way
            guild._member_ids.add(user_id)
        return member

    def delete_member(self, guild_id: "Snowflake_Type", user_id: "Snowflake_Type") -> None:
        """
        Delete a member from the cache.

        Args:
            guild_id: The ID of the guild this user belongs to
            user_id: The ID of the user
        """
        user_id = to_snowflake(user_id)
        guild_id = to_snowflake(guild_id)

        if member := self.member_cache.pop((guild_id, user_id), None):
            if member.guild:
                member.guild._member_ids.discard(user_id)

        self.delete_user_guild(user_id, guild_id)

    def place_user_guild(self, user_id: "Snowflake_Type", guild_id: "Snowflake_Type") -> None:
        """
        Add a guild to the list of guilds a user has joined.

        Args:
            user_id: The ID of the user
            guild_id: The ID of the guild to add
        """
        user_id = to_snowflake(user_id)
        guild_id = to_snowflake(guild_id)
        if user_id == self._client.user.id:
            # noinspection PyProtectedMember
            self._client.user._add_guilds({guild_id})
        else:
            guilds = self.user_guilds.get(user_id)
            if guilds:
                guilds.add(guild_id)
            else:
                guilds = {guild_id}
            self.user_guilds[user_id] = guilds

    def delete_user_guild(self, user_id: "Snowflake_Type", guild_id: "Snowflake_Type") -> None:
        """
        Remove a guild from the list of a guilds a user has joined.

        Args:
            user_id: The ID of the user
            guild_id: The ID of the guild to add
        """
        user_id = to_snowflake(user_id)
        guild_id = to_snowflake(guild_id)

        if user_id == self._client.user.id:
            # noinspection PyProtectedMember
            self._client.user._guild_ids.discard(guild_id)
        else:
            guilds = self.user_guilds.get(user_id)
            if guilds:
                guilds.discard(guild_id)
            else:
                guilds = {}
            self.user_guilds[user_id] = guilds

    async def is_user_in_guild(
        self,
        user_id: "Snowflake_Type",
        guild_id: "Snowflake_Type",
    ) -> bool:
        """
        Determine if a user is in a specified guild.

        Args:
            user_id: The ID of the user to check
            guild_id: The ID of the guild

        """
        user_id = to_snowflake(user_id)
        guild_id = to_snowflake(guild_id)

        # Try to get guild members list from the cache, without sending requests
        guild = self.get_guild(guild_id)
        if guild and (user_id in guild._member_ids):
            return True

        # If no such guild in cache or member not in guild cache, try to get member directly. May send requests
        try:
            member = await self.fetch_member(guild_id, user_id)
        except (NotFound, Forbidden):  # there is no such member in the guild (as per request)
            pass
        else:
            if member:
                return True

        return False

    async def fetch_user_guild_ids(self, user_id: "Snowflake_Type") -> List["Snowflake_Type"]:
        """
        Fetch a list of IDs for the guilds a user has joined.

        Args:
            user_id: The ID of the user

        Returns:
            A list of snowflakes for the guilds the client can see the user is within
        """
        user_id = to_snowflake(user_id)
        guild_ids = self.user_guilds.get(user_id)
        if not guild_ids:
            guild_ids = [
                guild_id for guild_id in self._client.user._guild_ids if await self.is_user_in_guild(user_id, guild_id)
            ]
            self.user_guilds[user_id] = set(guild_ids)
        return guild_ids

    def get_user_guild_ids(self, user_id: "Snowflake_Type") -> List["Snowflake_Type"]:
        """
        Get a list of IDs for the guilds the user has joined.

        Args:
            user_id: The ID of the user

        Returns:
            A list of snowflakes for the guilds the client can see the user is within
        """
        return list(self.user_guilds.get(to_snowflake(user_id)))

    # endregion Member cache

    # region Message cache

    async def fetch_message(
        self, channel_id: "Snowflake_Type", message_id: "Snowflake_Type", *, force: bool = False
    ) -> Message:
        """
        Fetch a message from a channel based on their IDs.

        Args:
            channel_id: The ID of the channel the message is in
            message_id: The ID of the message
            force: If the cache should be ignored, and the message should be fetched from the API

        Returns:
            The message if found
        """
        channel_id = to_snowflake(channel_id)
        message_id = to_snowflake(message_id)
        message = self.message_cache.get((channel_id, message_id))

        if message is None or force:
            data = await self._client.http.get_message(channel_id, message_id)
            message = self.place_message_data(data)
            if message.channel is None:
                await self.fetch_channel(channel_id)

            if not message.guild and isinstance(message.channel, GuildChannel):
                message._guild_id = message.channel._guild_id
        return message

    def get_message(
        self, channel_id: Optional["Snowflake_Type"], message_id: Optional["Snowflake_Type"]
    ) -> Optional[Message]:
        """
        Get a message from a channel based on their IDs.

        Args:
            channel_id: The ID of the channel the message is in
            message_id: The ID of the message

        Returns:
            The message if found
        """
        return self.message_cache.get((to_optional_snowflake(channel_id), to_optional_snowflake(message_id)))

    def place_message_data(self, data: discord_typings.MessageData) -> Message:
        """
        Take json data representing a message, process it, and cache it.

        Args:
            data: json representation of the message

        Returns:
            The processed message
        """
        channel_id = to_snowflake(data["channel_id"])
        message_id = to_snowflake(data["id"])
        message = self.message_cache.get((channel_id, message_id))
        if message is None:
            message = Message.from_dict(data, self._client)
            self.message_cache[(channel_id, message_id)] = message
        else:
            message.update_from_dict(data)
        return message

    def delete_message(self, channel_id: "Snowflake_Type", message_id: "Snowflake_Type") -> None:
        """
        Deletes a message from the cache.

        Args:
            channel_id: The ID of the channel the message is in
            message_id: The ID of the message
        """
        self.message_cache.pop((to_snowflake(channel_id), to_snowflake(message_id)), None)

    # endregion Message cache

    # region Channel cache
    async def fetch_channel(self, channel_id: "Snowflake_Type", *, force: bool = False) -> "TYPE_ALL_CHANNEL":
        """
        Get a channel based on its ID.

        Args:
            channel_id: The ID of the channel
            force: If the cache should be ignored, and the channel should be fetched from the API

        Returns:
            The channel if found
        """
        channel_id = to_snowflake(channel_id)
        channel = self.channel_cache.get(channel_id)
        if channel is None or force:
            try:
                data = await self._client.http.get_channel(channel_id)
                channel = self.place_channel_data(data)
            except Forbidden:
                self.logger.warning(f"Forbidden access to channel {channel_id}. Generating fallback channel object")
                channel = BaseChannel.from_dict({"id": channel_id, "type": MISSING}, self._client)
        return channel

    def get_channel(self, channel_id: Optional["Snowflake_Type"]) -> Optional["TYPE_ALL_CHANNEL"]:
        """
        Get a channel based on its ID.

        Args:
            channel_id: The ID of the channel

        Returns:
            The channel if found
        """
        return self.channel_cache.get(to_optional_snowflake(channel_id))

    def place_channel_data(self, data: discord_typings.ChannelData) -> "TYPE_ALL_CHANNEL":
        """
        Take json data representing a channel, process it, and cache it.

        Args:
            data: json representation of the channel

        Returns:
            The processed channel
        """
        channel_id = to_snowflake(data["id"])
        channel = self.channel_cache.get(channel_id)
        if channel is None:
            channel = BaseChannel.from_dict_factory(data, self._client)
            self.channel_cache[channel_id] = channel
            if guild := getattr(channel, "guild", None):
                if isinstance(channel, ThreadChannel):
                    guild._thread_ids.add(channel.id)
                elif isinstance(channel, GuildChannel):
                    guild._channel_ids.add(channel.id)
                guild._channel_gui_positions = {}
        else:
            # Create entire new channel object if the type changes
            channel_type = data.get("type", None)
            if channel_type and channel_type != channel.type:
                self.channel_cache.pop(channel_id)
                channel = BaseChannel.from_dict_factory(data, self._client)
            else:
                channel.update_from_dict(data)
                if guild := getattr(channel, "guild", None):
                    guild._channel_gui_positions = {}

        return channel

    def place_dm_channel_id(self, user_id: "Snowflake_Type", channel_id: "Snowflake_Type") -> None:
        """
        Cache that the bot is active within a DM channel.

        Args:
            user_id: The id of the user this DM channel belongs to
            channel_id: The id of the DM channel

        """
        self.dm_channels[to_snowflake(user_id)] = to_snowflake(channel_id)

    async def fetch_dm_channel_id(self, user_id: "Snowflake_Type", *, force: bool = False) -> "Snowflake_Type":
        """
        Get the DM channel ID for a user.

        Args:
            user_id: The ID of the user
            force: If the cache should be ignored, and the channel should be fetched from the API
        """
        user_id = to_snowflake(user_id)
        channel_id = self.dm_channels.get(user_id)
        if channel_id is None or force:
            data = await self._client.http.create_dm(user_id)
            channel = self.place_channel_data(data)
            channel_id = channel.id
        return channel_id

    async def fetch_dm_channel(self, user_id: "Snowflake_Type", *, force: bool = False) -> "DM":
        """
        Fetch the DM channel for a user.

        Args:
            user_id: The ID of the user
            force: If the cache should be ignored, and the channel should be fetched from the API
        """
        user_id = to_snowflake(user_id)
        channel_id = await self.fetch_dm_channel_id(user_id, force=force)
        return await self.fetch_channel(channel_id, force=force)

    def get_dm_channel(self, user_id: Optional["Snowflake_Type"]) -> Optional["DM"]:
        """
        Get the DM channel for a user.

        Args:
            user_id: The ID of the user
        """
        user_id = to_optional_snowflake(user_id)
        channel_id = self.dm_channels.get(user_id)
        return None if channel_id is None else self.get_channel(channel_id)

    def delete_channel(self, channel_id: "Snowflake_Type") -> None:
        """
        Delete a channel from the cache.

        Args:
            channel_id: The channel to be deleted
        """
        channel_id = to_snowflake(channel_id)
        channel = self.channel_cache.pop(channel_id, None)
        if guild := getattr(channel, "guild", None):
            if isinstance(channel, ThreadChannel):
                guild._thread_ids.discard(channel.id)
            elif isinstance(channel, GuildChannel):
                guild._channel_ids.discard(channel.id)
            guild._channel_gui_positions = {}

    # endregion Channel cache

    # region Guild cache

    async def fetch_guild(self, guild_id: "Snowflake_Type", *, force: bool = False) -> Guild:
        """
        Fetch a guild based on its ID.

        Args:
            guild_id: The ID of the guild
            force: If the cache should be ignored, and the guild should be fetched from the API

        Returns:
            The guild if found
        """
        guild_id = to_snowflake(guild_id)
        guild = self.guild_cache.get(guild_id)
        if guild is None or force:
            data = await self._client.http.get_guild(guild_id)
            guild = self.place_guild_data(data)
        return guild

    def get_guild(self, guild_id: Optional["Snowflake_Type"]) -> Optional[Guild]:
        """
        Get a guild based on its ID.

        Args:
            guild_id: The ID of the guild.

        Returns:
            The guild if found
        """
        return self.guild_cache.get(to_optional_snowflake(guild_id))

    def place_guild_data(self, data: discord_typings.GuildData) -> Guild:
        """
        Take json data representing a guild, process it, and cache it.

        Args:
            data: json representation of the guild

        Returns:
            The processed guild
        """
        guild_id = to_snowflake(data["id"])
        guild: Guild = self.guild_cache.get(guild_id)
        if guild is None:
            guild = Guild.from_dict(data, self._client)
            self.guild_cache[guild_id] = guild
        else:
            guild.update_from_dict(data)
        return guild

    def delete_guild(self, guild_id: "Snowflake_Type") -> None:
        """
        Delete a guild from the cache.

        Args:
            guild_id: The ID of the guild
        """
        if guild := self.guild_cache.pop(to_snowflake(guild_id), None):
            # delete associated objects
            [self.delete_channel(c) for c in guild.channels]
            [self.delete_member(m.id, guild_id) for m in guild.members]
            [self.delete_role(r) for r in guild.roles]
            if self.enable_emoji_cache:  # todo: this is ungodly slow, find a better way to do this
                for emoji in self.emoji_cache.values():
                    if emoji._guild_id == guild_id:
                        self.delete_emoji(emoji)

    # endregion Guild cache

    # region Roles cache

    async def fetch_role(
        self,
        guild_id: "Snowflake_Type",
        role_id: "Snowflake_Type",
        *,
        force: bool = False,
    ) -> Role:
        """
        Fetch a role based on the guild and its own ID.

        Args:
            guild_id: The ID of the guild this role belongs to
            role_id: The ID of the role
            force: If the cache should be ignored, and the role should be fetched from the API

        Returns:
            The role if found
        """
        guild_id = to_snowflake(guild_id)
        role_id = to_snowflake(role_id)
        role = self.role_cache.get(role_id)
        if role is None or force:
            data = await self._client.http.get_roles(guild_id)
            role = self.place_role_data(guild_id, data).get(role_id)
        return role

    def get_role(self, role_id: Optional["Snowflake_Type"]) -> Optional[Role]:
        """
        Get a role based on the role ID.

        Args:
            role_id: The ID of the role

        Returns:
            The role if found
        """
        return self.role_cache.get(to_optional_snowflake(role_id))

    def place_role_data(
        self, guild_id: "Snowflake_Type", data: List[Dict["Snowflake_Type", Any]]
    ) -> Dict["Snowflake_Type", Role]:
        """
        Take json data representing a role, process it, and cache it.

        Can handle multiple roles at once

        Args:
            guild_id: The ID of the guild this role belongs to
            data: json representation of the role

        Returns:
            The processed role
        """
        guild_id = to_snowflake(guild_id)

        roles: Dict["Snowflake_Type", Role] = {}
        for role_data in data:  # todo not update cache expiration order for roles
            role_data.update({"guild_id": guild_id})
            role_id = to_snowflake(role_data["id"])

            role = self.role_cache.get(role_id)
            if role is None:
                role = Role.from_dict(role_data, self._client)
                self.role_cache[role_id] = role
            else:
                role.update_from_dict(role_data)

            roles[role_id] = role

        return roles

    def delete_role(self, role_id: "Snowflake_Type") -> None:
        """
        Delete a role from the cache.

        Args:
            role_id: The ID of the role
        """
        if role := self.role_cache.pop(to_snowflake(role_id), None):
            if guild := self.get_guild(role._guild_id):
                # noinspection PyProtectedMember
                guild._role_ids.discard(role_id)

    # endregion Role cache

    # region Voice cache

    def get_voice_state(self, user_id: Optional["Snowflake_Type"]) -> Optional[VoiceState]:
        """
        Get a voice state by their guild and user IDs.

        Args:
            user_id: The ID of the user

        Returns:
            VoiceState object if found

        """
        return self.voice_state_cache.get(to_optional_snowflake(user_id))

    async def place_voice_state_data(
        self, data: discord_typings.VoiceStateData, update_cache=True
    ) -> Optional[VoiceState]:
        """
        Take json data representing a VoiceState, process it, and cache it.

        Args:
            data: json representation of the VoiceState
            update_cache: Bool for updating cache or not

        Returns:
            The processed VoiceState object
        """
        user_id = to_snowflake(data["user_id"])

        if old_state := self.get_voice_state(user_id):
            # noinspection PyProtectedMember
            if user_id in old_state.channel._voice_member_ids:
                # noinspection PyProtectedMember
                old_state.channel._voice_member_ids.remove(user_id)

        # check if the channel_id is None
        # if that is the case, the user disconnected, and we can delete them from the cache
        if not data["channel_id"]:
            if update_cache and user_id in self.voice_state_cache:
                self.voice_state_cache.pop(user_id)
            voice_state = None

        # this means the user swapped / joined a channel
        else:
            # update the _voice_member_ids of the new channel
            new_channel = await self.fetch_channel(data["channel_id"])
            # noinspection PyProtectedMember
            new_channel._voice_member_ids.append(user_id)

            voice_state = VoiceState.from_dict(data, self._client)
            if update_cache:
                self.voice_state_cache[user_id] = voice_state

        return voice_state

    def delete_voice_state(self, user_id: "Snowflake_Type") -> None:
        """
        Delete a voice state from the cache.

        Args:
            user_id: The ID of the user
        """
        self.voice_state_cache.pop(to_snowflake(user_id), None)

    # endregion Voice cache

    # region Bot Voice cache

    def get_bot_voice_state(self, guild_id: Optional["Snowflake_Type"]) -> Optional[ActiveVoiceState]:
        """
        Get a voice state for the bot, by the guild id.

        Args:
            guild_id: The id of the guild

        Returns:
            ActiveVoiceState if found
        """
        return self.bot_voice_state_cache.get(to_optional_snowflake(guild_id))

    def place_bot_voice_state(self, state: ActiveVoiceState) -> None:
        """
        Place an ActiveVoiceState into the cache.

        Args:
            state: The voice state to cache
        """
        if state._guild_id is None:
            return

        # noinspection PyProtectedMember
        self.bot_voice_state_cache[to_snowflake(state._guild_id)] = state

    def delete_bot_voice_state(self, guild_id: "Snowflake_Type") -> None:
        """
        Delete an ActiveVoiceState from the cache.

        Args:
            guild_id: The id of the guild
        """
        self.bot_voice_state_cache.pop(to_snowflake(guild_id), None)

    # endregion Bot Voice cache

    # region Emoji cache

    async def fetch_emoji(
        self, guild_id: "Snowflake_Type", emoji_id: "Snowflake_Type", *, force: bool = False
    ) -> "CustomEmoji":
        """
        Fetch an emoji based on the guild and its own ID.

        This cache is disabled by default, start your bot with `Client(enable_emoji_cache=True)` to enable it.

        Args:
            guild_id: The ID of the guild this emoji belongs to
            emoji_id: The ID of the emoji
            force: If the cache should be ignored, and the emoji should be fetched from the API

        Returns:
            The Emoji if found
        """
        guild_id = to_snowflake(guild_id)
        emoji_id = to_snowflake(emoji_id)
        emoji = self.emoji_cache.get(emoji_id) if self.emoji_cache is not None else None
        if emoji is None or force:
            data = await self._client.http.get_guild_emoji(guild_id, emoji_id)
            emoji = self.place_emoji_data(guild_id, data)

        return emoji

    def get_emoji(self, emoji_id: Optional["Snowflake_Type"]) -> Optional["CustomEmoji"]:
        """
        Get an emoji based on the emoji ID.

        This cache is disabled by default, start your bot with `Client(enable_emoji_cache=True)` to enable it.

        Args:
            emoji_id: The ID of the emoji

        Returns:
            The Emoji if found
        """
        return self.emoji_cache.get(to_optional_snowflake(emoji_id)) if self.emoji_cache is not None else None

    def place_emoji_data(self, guild_id: "Snowflake_Type", data: discord_typings.EmojiData) -> "CustomEmoji":
        """
        Take json data representing an emoji, process it, and cache it. This cache is disabled by default, start your bot with `Client(enable_emoji_cache=True)` to enable it.

        Args:
            guild_id: The ID of the guild this emoji belongs to
            data: json representation of the emoji

        Returns:
            The processed emoji
        """
        with suppress(KeyError):
            del data["guild_id"]  # discord sometimes packages a guild_id - this will cause an exception

        emoji = CustomEmoji.from_dict(data, self._client, to_snowflake(guild_id))
        if self.emoji_cache is not None:
            self.emoji_cache[emoji.id] = emoji

        return emoji

    def delete_emoji(self, emoji_id: "Snowflake_Type") -> None:
        """
        Delete an emoji from the cache.

        Args:
            emoji_id: The ID of the emoji
        """
        if self.emoji_cache is not None:
            self.emoji_cache.pop(to_snowflake(emoji_id), None)

    # endregion Emoji cache

    # region ScheduledEvents cache

    def get_scheduled_event(self, scheduled_event_id: "Snowflake_Type") -> Optional["ScheduledEvent"]:
        """
        Get a scheduled event based on the scheduled event ID.

        Args:
            scheduled_event_id: The ID of the scheduled event

        Returns:
            The ScheduledEvent if found
        """
        return self.scheduled_events_cache.get(to_snowflake(scheduled_event_id))

    async def fetch_scheduled_event(
        self,
        guild_id: "Snowflake_Type",
        scheduled_event_id: "Snowflake_Type",
        with_user_count: bool = False,
        *,
        force: bool = False,
    ) -> "ScheduledEvent":
        """
        Fetch a scheduled event based on the guild and its own ID.

        Args:
            guild_id: The ID of the guild this event belongs to
            scheduled_event_id: The ID of the event
            with_user_count: Whether to include the user count in the response.
            force: If the cache should be ignored, and the event should be fetched from the API

        Returns:
            The scheduled event if found
        """
        if not force:
            if scheduled_event := self.get_scheduled_event(scheduled_event_id):
                if int(scheduled_event._guild_id) == int(guild_id) and (
                    not with_user_count or scheduled_event.user_count is not MISSING
                ):
                    return scheduled_event

        scheduled_event_data = await self._client.http.get_scheduled_event(
            guild_id, scheduled_event_id, with_user_count=with_user_count
        )
        return self.place_scheduled_event_data(scheduled_event_data)

    def place_scheduled_event_data(self, data: discord_typings.GuildScheduledEventData) -> "ScheduledEvent":
        """
        Take json data representing a scheduled event, process it, and cache it.

        Args:
            data: json representation of the scheduled event

        Returns:
            The processed scheduled event
        """
        scheduled_event = ScheduledEvent.from_dict(data, self._client)
        self.scheduled_events_cache[scheduled_event.id] = scheduled_event

        return scheduled_event

    def delete_scheduled_event(self, scheduled_event_id: "Snowflake_Type") -> None:
        """
        Delete a scheduled event from the cache.

        Args:
            scheduled_event_id: The ID of the scheduled event
        """
        self.scheduled_events_cache.pop(to_snowflake(scheduled_event_id), None)

    # endregion ScheduledEvents cache
