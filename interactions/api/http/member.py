from typing import List, Optional

from ...api.cache import Cache
from .request import _Request
from .route import Route


class MemberRequest:

    _req: _Request
    cache: Cache

    def __init__(self) -> None:
        pass

    async def get_member(self, guild_id: int, member_id: int) -> Optional[dict]:
        """
        Uses the API to fetch a member from a guild.

        :param guild_id: Guild ID snowflake.
        :param member_id: Member ID snowflake.
        :return: A member object, if any.
        """
        return await self._req.request(
            Route(
                "GET",
                "/guilds/{guild_id}/members/{member_id}",
                guild_id=guild_id,
                member_id=member_id,
            )
        )

    async def get_list_of_members(
        self, guild_id: int, limit: int = 1, after: Optional[int] = None
    ) -> List[dict]:
        """
        Lists the members of a guild.

        :param guild_id: Guild ID snowflake
        :param limit: How many members to get from the API. Max is 1000. Defaults to 1.
        :param after: Get Member IDs after this snowflake. Defaults to None.
        :return: An array of Member objects.
        """
        payload = {"limit": limit}
        if after:
            payload["after"] = after

        return await self._req.request(Route("GET", f"/guilds/{guild_id}/members"), params=payload)

    async def search_guild_members(self, guild_id: int, query: str, limit: int = 1) -> List[dict]:
        """
        Search a guild for members whose username or nickname starts with provided string.

        :param guild_id: Guild ID snowflake.
        :param query: The string to search for
        :param limit: The number of members to return. Defaults to 1.
        """

        return await self._req.request(
            Route("GET", f"/guilds/{guild_id}/members/search"),
            params={"query": query, "limit": limit},
        )

    async def add_member_role(
        self, guild_id: int, user_id: int, role_id: int, reason: Optional[str] = None
    ) -> None:
        """
        Adds a role to a guild member.

        :param guild_id: The ID of the guild
        :param user_id: The ID of the user
        :param role_id: The ID of the role to add
        :param reason: The reason for this action. Defaults to None.
        """
        return await self._req.request(
            Route(
                "PUT",
                "/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
                guild_id=guild_id,
                user_id=user_id,
                role_id=role_id,
            ),
            reason=reason,
        )

    async def remove_member_role(
        self, guild_id: int, user_id: int, role_id: int, reason: Optional[str] = None
    ) -> None:
        """
        Removes a role to a guild member.

        :param guild_id: The ID of the guild
        :param user_id: The ID of the user
        :param role_id: The ID of the role to add
        :param reason: The reason for this action. Defaults to None.
        """
        return await self._req.request(
            Route(
                "DELETE",
                "/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
                guild_id=guild_id,
                user_id=user_id,
                role_id=role_id,
            ),
            reason=reason,
        )

    async def modify_member(
        self, user_id: int, guild_id: int, payload: dict, reason: Optional[str] = None
    ) -> dict:
        """
        Edits a member.
        This can nick them, change their roles, mute/deafen (and its contrary), and moving them across channels and/or disconnect them.

        :param user_id: Member ID snowflake.
        :param guild_id: Guild ID snowflake.
        :param payload: Payload representing parameters (nick, roles, mute, deaf, channel_id)
        :param reason: The reason for this action. Defaults to None.
        :return: Modified member object.
        """

        return await self._req.request(
            Route(
                "PATCH", "/guilds/{guild_id}/members/{user_id}", guild_id=guild_id, user_id=user_id
            ),
            json=payload,
            reason=reason,
        )
