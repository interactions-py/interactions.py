from typing import TYPE_CHECKING, Any, List

import discord_typings

from ..route import Route

__all__ = ("UserRequests",)


if TYPE_CHECKING:
    from interactions.models.discord.snowflake import Snowflake_Type


class UserRequests:
    request: Any

    async def get_current_user(self) -> discord_typings.UserData:
        """
        Shortcut to get requester's user.

        Returns:
            The user object.

        """
        return await self.get_user("@me")

    async def get_user(self, user_id: "Snowflake_Type") -> discord_typings.UserData:
        """
        Get a user object for a given user ID.

        Args:
            user_id: The user to get.

        Returns:
            The user object.

        """
        return await self.request(Route("GET", "/users/{user_id}", user_id=user_id))

    async def modify_client_user(self, payload: dict) -> discord_typings.UserData:
        """
        Modify the user account settings.

        Args:
            payload: The data to send.

        """
        return await self.request(Route("PATCH", "/users/@me"), payload=payload)

    async def get_user_guilds(self) -> List[discord_typings.GuildData]:
        """
        Returns a list of partial guild objects the current user is a member of.

        Requires the guilds OAuth2 scope.

        """
        return await self.request(Route("GET", "/users/@me/guilds"))

    async def leave_guild(self, guild_id: "Snowflake_Type") -> None:
        """
        Leave a guild. Returns a 204 empty response on success.

        Args:
            guild_id: The guild to leave from.

        """
        return await self.request(Route("DELETE", "/users/@me/guilds/{guild_id}", guild_id=guild_id))

    async def create_dm(self, recipient_id: "Snowflake_Type") -> discord_typings.DMChannelData:
        """
        Create a new DM channel with a user. Returns a DM channel object.

        Args:
            recipient_id: The recipient to open a DM channel with.

        """
        return await self.request(Route("POST", "/users/@me/channels"), payload={"recipient_id": recipient_id})

    async def create_group_dm(self, payload: dict) -> discord_typings.GroupDMChannelData:
        """
        Create a new group DM channel with multiple users.

        Args:
            payload: The data to send.

        """
        return await self.request(Route("POST", "/users/@me/channels"), payload=payload)

    async def get_user_connections(self) -> list:
        """
        Returns a list of connection objects.

        Requires the connections OAuth2 scope.

        """
        return await self.request(Route("GET", "/users/@me/connections"))

    async def group_dm_add_recipient(
        self,
        channel_id: "Snowflake_Type",
        user_id: "Snowflake_Type",
        access_token: str,
        nick: str | None = None,
    ) -> None:
        """
        Adds a recipient to a Group DM using their access token.

        Args:
            channel_id: The ID of the group dm
            user_id: The ID of the user to add
            access_token: Access token of a user that has granted your app the gdm.join scope
            nick: Nickname of the user being added

        """
        return await self.request(
            Route("PUT", "/channels/{channel_id}/recipients/{user_id}", channel_id=channel_id, user_id=user_id),
            payload={"access_token": access_token, "nick": nick},
        )

    async def group_dm_remove_recipient(self, channel_id: "Snowflake_Type", user_id: "Snowflake_Type") -> None:
        """
        Remove a recipient from the group dm.

        Args:
            channel_id: The ID of the group dm
            user_id: The ID of the user to remove

        """
        return await self.request(
            Route("DELETE", "/channels/{channel_id}/recipients/{user_id}", channel_id=channel_id, user_id=user_id)
        )

    async def modify_current_user_nick(self, guild_id: "Snowflake_Type", nickname: str | None = None) -> None:
        """
        Modifies the nickname of the current user in a guild.

        Args:
            guild_id: The ID of the guild
            nickname: The new nickname to use

        """
        return await self.request(
            Route("PATCH", "/guilds/{guild_id}/members/@me/nick", guild_id=guild_id), payload={"nick": nickname}
        )
