from typing import TYPE_CHECKING, Any, List

import discord_typings

from interactions.client.const import MISSING, Absent
from interactions.models.discord.snowflake import to_snowflake
from ..route import Route

__all__ = ("ReactionRequests",)


if TYPE_CHECKING:
    from interactions.models.discord.snowflake import Snowflake_Type


class ReactionRequests:
    request: Any

    async def create_reaction(self, channel_id: "Snowflake_Type", message_id: "Snowflake_Type", emoji: str) -> None:
        """
        Create a reaction for a message.

        Args:
            channel_id: The channel this is taking place in
            message_id: The message to create a a reaction on
            emoji: The emoji to use (format: `name:id`)

        """
        return await self.request(
            Route(
                "PUT",
                "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
            )
        )

    async def remove_self_reaction(
        self, channel_id: "Snowflake_Type", message_id: "Snowflake_Type", emoji: str
    ) -> None:
        """
        Remove client's reaction from a message.

        Args:
            channel_id: The channel this is taking place in.
            message_id: The message to remove the reaction on.
            emoji: The emoji to remove. (format: `name:id`)

        """
        return await self.request(
            Route(
                "DELETE",
                "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
            )
        )

    async def remove_user_reaction(
        self,
        channel_id: "Snowflake_Type",
        message_id: "Snowflake_Type",
        emoji: str,
        user_id: "Snowflake_Type",
    ) -> None:
        """
        Remove user's reaction from a message.

        Args:
            channel_id: The channel this is taking place in
            message_id: The message to remove the reaction on.
            emoji: The emoji to remove. (format: `name:id`)
            user_id: The user to remove reaction of.

        """
        return await self.request(
            Route(
                "DELETE",
                "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}",
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
                user_id=user_id,
            )
        )

    async def clear_reaction(self, channel_id: "Snowflake_Type", message_id: "Snowflake_Type", emoji: str) -> None:
        """
        Remove specific reaction from a message.

        Args:
            channel_id: The channel this is taking place in.
            message_id: The message to remove the reaction on.
            emoji: The emoji to remove. (format: `name:id`)

        """
        return await self.request(
            Route(
                "DELETE",
                "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}",
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
            )
        )

    async def clear_reactions(self, channel_id: "Snowflake_Type", message_id: "Snowflake_Type") -> None:
        """
        Remove reactions from a message.

        Args:
            channel_id: The channel this is taking place in.
            message_id: The message to clear reactions from.

        """
        return await self.request(
            Route(
                "DELETE",
                "/channels/{channel_id}/messages/{message_id}/reactions",
                channel_id=channel_id,
                message_id=message_id,
            )
        )

    async def get_reactions(
        self,
        channel_id: "Snowflake_Type",
        message_id: "Snowflake_Type",
        emoji: str,
        limit: Absent[int] = MISSING,
        after: "Snowflake_Type" = MISSING,
    ) -> List[discord_typings.UserData]:
        """
        Gets specific reaction from a message.

        Args:
            channel_id: The channel this is taking place in.
            message_id: The message to get the reaction.
            emoji: The emoji to get. (format: `name:id`)
            limit: max number of entries to get
            after: snowflake to get entries after

        Returns:
            List of users who reacted with the emoji.

        """
        return await self.request(
            Route(
                "GET",
                "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}",
                channel_id=to_snowflake(channel_id),
                message_id=to_snowflake(message_id),
                emoji=emoji,
            ),
            params={"limit": limit, "after": after},
        )
