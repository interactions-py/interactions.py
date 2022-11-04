from typing import TYPE_CHECKING, List

from .request import _Request
from .route import Route

if TYPE_CHECKING:
    from ...api.cache import Cache

__all__ = ("ReactionRequest",)


class ReactionRequest:
    _req: _Request
    cache: "Cache"

    def __init__(self) -> None:
        pass

    async def create_reaction(self, channel_id: int, message_id: int, emoji: str) -> None:
        """
        Create a reaction for a message.

        :param channel_id: Channel snowflake ID.
        :param message_id: Message snowflake ID.
        :param emoji: The emoji to use (format: `name:id`)
        """
        return await self._req.request(
            Route(
                "PUT",
                "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
            )
        )

    async def remove_self_reaction(self, channel_id: int, message_id: int, emoji: str) -> None:
        """
        Remove bot user's reaction from a message.

        :param channel_id: Channel snowflake ID.
        :param message_id: Message snowflake ID.
        :param emoji: The emoji to remove (format: `name:id`)
        """
        return await self._req.request(
            Route(
                "DELETE",
                "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
            )
        )

    async def remove_user_reaction(
        self, channel_id: int, message_id: int, emoji: str, user_id: int
    ) -> None:
        """
        Remove user's reaction from a message.

        :param channel_id: The channel this is taking place in
        :param message_id: The message to remove the reaction on.
        :param emoji: The emoji to remove. (format: `name:id`)
        :param user_id: The user to remove reaction of.
        """
        return await self._req.request(
            Route(
                "DELETE",
                "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}",
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
                user_id=user_id,
            )
        )

    async def remove_all_reactions(self, channel_id: int, message_id: int) -> None:
        """
        Remove all reactions from a message.

        :param channel_id: The channel this is taking place in.
        :param message_id: The message to clear reactions from.
        """
        return await self._req.request(
            Route(
                "DELETE",
                "/channels/{channel_id}/messages/{message_id}/reactions",
                channel_id=channel_id,
                message_id=message_id,
            )
        )

    async def remove_all_reactions_of_emoji(
        self, channel_id: int, message_id: int, emoji: str
    ) -> None:
        """
        Remove all reactions of a certain emoji from a message.

        :param channel_id: Channel snowflake ID.
        :param message_id: Message snowflake ID.
        :param emoji: The emoji to remove (format: `name:id`)
        """
        return await self._req.request(
            Route(
                "DELETE",
                "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}",
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
            )
        )

    async def get_reactions_of_emoji(
        self,
        channel_id: int,
        message_id: int,
        emoji: str,
        limit: int = 25,
        after: int = None,
    ) -> List[dict]:
        """
        Gets the users who reacted to the emoji.

        :param channel_id: Channel snowflake ID.
        :param message_id: Message snowflake ID.
        :param emoji: The emoji to get (format: `name:id`)
        :param limit: Max number of users to return (1-100)
        :param after: Get users after this user ID
        :return: A list of users who sent that emoji.
        """

        params_set = {
            f"after={after}" if after else None,
            f"limit={limit}",
        }
        final = "&".join([item for item in params_set if item is not None])

        return await self._req.request(
            Route(
                "GET",
                (
                    "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}"
                    + f"{f'?{final}' if final is not None else ''}"
                ),
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
            )
        )
