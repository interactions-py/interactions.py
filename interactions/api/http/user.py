from typing import Optional

from ...api.cache import Cache
from ..models.channel import Channel
from ..models.user import User
from .request import _Request
from .route import Route

__all__ = ("UserRequest",)


class UserRequest:
    _req: _Request
    cache: Cache

    def __init__(self) -> None:
        pass

    async def get_self(self) -> dict:
        """
        An alias to `get_user`, but only gets the current bot user.

        :return: A partial User object of the current bot user in the form of a dictionary.
        """
        return await self.get_user()

    async def get_user(self, user_id: Optional[int] = None) -> dict:
        """
        Gets a user object for a given user ID.

        :param user_id: A user snowflake ID. If omitted, this defaults to the current bot user.
        :return: A partial User object in the form of a dictionary.
        """

        if user_id is None:
            user_id = "@me"

        request = await self._req.request(Route("GET", f"/users/{user_id}"))
        self.cache[User].add(User(**request))

        return request

    async def modify_self(self, payload: dict) -> dict:
        """
        Modify the bot user account settings.

        :param payload: The data to send.
        """
        return await self._req.request(Route("PATCH", "/users/@me"), json=payload)

    async def modify_self_nick_in_guild(self, guild_id: int, nickname: Optional[str]) -> dict:
        """
        Changes a nickname of the current bot user in a guild.

        :param guild_id: Guild snowflake ID.
        :param nickname: The new nickname, if any.
        :return: Nothing needed to be yielded.
        """
        return await self._req.request(
            Route(
                "PATCH", "/guilds/{guild_id}/members/@me", guild_id=guild_id
            ),  # /nick is deprecated
            json={"nick": nickname},
        )

    async def create_dm(self, recipient_id: int) -> dict:
        """
        Creates a new DM channel with a user.

        :param recipient_id: User snowflake ID.
        :return: Returns a dictionary representing a DM Channel object.
        """
        # only named recipient_id because of api mirroring

        request = await self._req.request(
            Route("POST", "/users/@me/channels"), json={"recipient_id": recipient_id}
        )
        self.cache[Channel].add(Channel(**request))

        return request
