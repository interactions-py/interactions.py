from typing import TYPE_CHECKING, cast

import discord_typings

from interactions.models.internal.protocols import CanRequest
from ..route import Route

__all__ = ("MessageRequests",)


if TYPE_CHECKING:
    from interactions.models.discord.snowflake import Snowflake_Type
    from interactions import UPLOADABLE_TYPE


class MessageRequests(CanRequest):
    async def create_message(
        self,
        payload: dict,
        channel_id: "Snowflake_Type",
        files: list["UPLOADABLE_TYPE"] | None = None,  # todo type payload
    ) -> discord_typings.MessageData:
        """
        Send a message to the specified channel.

        Args:
            payload: The message to send
            channel_id: id of the channel to send message in
            files: Any files to send with this message

        Returns:
            The resulting message object

        """
        result = await self.request(
            Route("POST", "/channels/{channel_id}/messages", channel_id=channel_id), payload=payload, files=files
        )
        return cast(discord_typings.MessageData, result)

    async def delete_message(
        self, channel_id: "Snowflake_Type", message_id: "Snowflake_Type", reason: str | None = None
    ) -> None:
        """
        Deletes a message from the specified channel.

        Args:
            channel_id: The id of the channel to delete the message from
            message_id: The id of the message to delete
            reason: The reason for this action

        """
        await self.request(
            Route(
                "DELETE", "/channels/{channel_id}/messages/{message_id}", channel_id=channel_id, message_id=message_id
            ),
            reason=reason,
        )

    async def bulk_delete_messages(
        self,
        channel_id: "Snowflake_Type",
        message_ids: list["Snowflake_Type"],
        reason: str | None = None,
    ) -> None:
        """
        Delete multiple messages in a single request.

        Args:
            channel_id: The id of the channel these messages are in
            message_ids: A list of message ids to delete
            reason: The reason for this action

        """
        payload = {"messages": [int(message_id) for message_id in message_ids]}

        await self.request(
            Route("POST", "/channels/{channel_id}/messages/bulk-delete", channel_id=channel_id),
            payload=payload,
            reason=reason,
        )

    async def get_message(
        self, channel_id: "Snowflake_Type", message_id: "Snowflake_Type"
    ) -> discord_typings.MessageData:
        """
        Get a specific message in the channel. Returns a message object on success.

        Args:
            channel_id: the channel this message belongs to
            message_id: the id of the message

        Returns:
            message or None

        """
        result = await self.request(
            Route("GET", "/channels/{channel_id}/messages/{message_id}", channel_id=channel_id, message_id=message_id)
        )
        return cast(discord_typings.MessageData, result)

    async def pin_message(self, channel_id: "Snowflake_Type", message_id: "Snowflake_Type") -> None:
        """
        Pin a message to a channel.

        Args:
            channel_id: Channel to pin message to
            message_id: Message to pin

        """
        await self.request(
            Route("PUT", "/channels/{channel_id}/pins/{message_id}", channel_id=channel_id, message_id=message_id)
        )

    async def unpin_message(self, channel_id: "Snowflake_Type", message_id: "Snowflake_Type") -> None:
        """
        Unpin a message to a channel.

        Args:
            channel_id: Channel to unpin message to
            message_id: Message to unpin

        """
        await self.request(
            Route("DELETE", "/channels/{channel_id}/pins/{message_id}", channel_id=channel_id, message_id=message_id)
        )

    async def edit_message(
        self,
        payload: dict,
        channel_id: "Snowflake_Type",
        message_id: "Snowflake_Type",
        files: list["UPLOADABLE_TYPE"] | None = None,
    ) -> discord_typings.MessageData:
        """
        Edit an existing message.

        Args:
            payload:
            channel_id: Channel of message to edit.
            message_id: Message to edit.
            files: Any files to send with this message

        Returns:
            Message object of edited message

        """
        result = await self.request(
            Route(
                "PATCH", "/channels/{channel_id}/messages/{message_id}", channel_id=channel_id, message_id=message_id
            ),
            payload=payload,
            files=files,
        )
        return cast(discord_typings.MessageData, result)

    async def crosspost_message(
        self, channel_id: "Snowflake_Type", message_id: "Snowflake_Type"
    ) -> discord_typings.MessageData:
        """
        Crosspost a message in a News Channel to following channels.

        Args:
            channel_id: Channel the message is in
            message_id: The id of the message to crosspost
        Returns:
            message object

        """
        result = await self.request(
            Route(
                "POST",
                "/channels/{channel_id}/messages/{message_id}/crosspost",
                channel_id=channel_id,
                message_id=message_id,
            )
        )
        return cast(discord_typings.MessageData, result)
