from typing import TYPE_CHECKING, Any, List, Optional

import discord_typings
from aiohttp import FormData

from interactions.api.http.route import Route
from interactions.client.const import MISSING, Absent
from interactions.models.discord.enums import ChannelType
from interactions.models.discord.timestamp import Timestamp

__all__ = ("ThreadRequests",)


if TYPE_CHECKING:
    from interactions.models.discord.snowflake import Snowflake_Type
    from interactions import UPLOADABLE_TYPE


class ThreadRequests:
    request: Any

    async def join_thread(self, thread_id: "Snowflake_Type") -> None:
        """
        Join a thread.

        Args:
            thread_id: The thread to join.

        """
        return await self.request(Route("PUT", "/channels/{thread_id}/thread-members/@me", thread_id=thread_id))

    async def leave_thread(self, thread_id: "Snowflake_Type") -> None:
        """
        Leave a thread.

        Args:
            thread_id: The thread to leave.

        """
        return await self.request(Route("DELETE", "/channels/{thread_id}/thread-members/@me", thread_id=thread_id))

    async def add_thread_member(self, thread_id: "Snowflake_Type", user_id: "Snowflake_Type") -> None:
        """
        Add another user to a thread.

        Args:
            thread_id: The ID of the thread
            user_id: The ID of the user to add

        """
        return await self.request(
            Route("PUT", "/channels/{thread_id}/thread-members/{user_id}", thread_id=thread_id, user_id=user_id)
        )

    async def remove_thread_member(self, thread_id: "Snowflake_Type", user_id: "Snowflake_Type") -> None:
        """
        Remove another user from a thread.

        Args:
            thread_id: The ID of the thread
            user_id: The ID of the user to remove

        """
        return await self.request(
            Route("DELETE", "/channels/{thread_id}/thread-members/{user_id}", thread_id=thread_id, user_id=user_id)
        )

    async def list_thread_members(self, thread_id: "Snowflake_Type") -> List[discord_typings.ThreadMemberData]:
        """
        Get a list of members in the thread.

        Args:
            thread_id: the id of the thread

        Returns:
            a list of member objects

        """
        return await self.request(Route("GET", "/channels/{thread_id}/thread-members", thread_id=thread_id))

    async def list_public_archived_threads(
        self,
        channel_id: "Snowflake_Type",
        limit: int = None,
        before: Optional["Snowflake_Type"] = None,
    ) -> discord_typings.ListThreadsData:
        """
        Get a list of archived public threads in a channel.

        Args:
            channel_id: The channel to get threads from
            limit: Optional limit of threads to
            before: Get threads before this snowflake

        Returns:
            a list of threads

        """
        payload = {}
        if limit:
            payload["limit"] = limit
        if before:
            payload["before"] = Timestamp.from_snowflake(before).isoformat()
        return await self.request(
            Route("GET", "/channels/{channel_id}/threads/archived/public", channel_id=channel_id), params=payload
        )

    async def list_private_archived_threads(
        self,
        channel_id: "Snowflake_Type",
        limit: int = None,
        before: Optional["Snowflake_Type"] = None,
    ) -> discord_typings.ListThreadsData:
        """
        Get a list of archived private threads in a channel.

        Args:
            channel_id: The channel to get threads from
            limit: Optional limit of threads to
            before: Get threads before this snowflake

        Returns:
            a list of threads

        """
        payload = {}
        if limit:
            payload["limit"] = limit
        if before:
            payload["before"] = Timestamp.from_snowflake(before).isoformat()
        return await self.request(
            Route("GET", "/channels/{channel_id}/threads/archived/private", channel_id=channel_id), params=payload
        )

    async def list_joined_private_archived_threads(
        self,
        channel_id: "Snowflake_Type",
        limit: int = None,
        before: Optional["Snowflake_Type"] = None,
    ) -> discord_typings.ListThreadsData:
        """
        Get a list of archived private threads in a channel that you have joined.

        Args:
            channel_id: The channel to get threads from
            limit: Optional limit of threads to
            before: Get threads before this snowflake

        Returns:
            a list of threads

        """
        payload = {}
        if limit:
            payload["limit"] = limit
        if before:
            payload["before"] = before
        return await self.request(
            Route("GET", "/channels/{channel_id}/users/@me/threads/archived/private", channel_id=channel_id),
            params=payload,
        )

    async def list_active_threads(self, guild_id: "Snowflake_Type") -> discord_typings.ListThreadsData:
        """
        List active threads within a guild.

        Args:
            guild_id: the guild id to get threads from

        Returns:
            A list of active threads

        """
        return await self.request(Route("GET", "/guilds/{guild_id}/threads/active", guild_id=guild_id))

    async def create_thread(
        self,
        channel_id: "Snowflake_Type",
        name: str,
        auto_archive_duration: int,
        thread_type: Absent[int] = MISSING,
        invitable: Absent[bool] = MISSING,
        rate_limit_per_user: Absent[int] = MISSING,
        message_id: Absent["Snowflake_Type"] = MISSING,
        reason: Absent[str] = MISSING,
    ) -> discord_typings.ThreadChannelData:
        """
        Create a thread in the given channel. Can either create a thread with or without a message.

        Args:
            channel_id: The ID of the channel to create this thread in
            name: The name of the thread
            auto_archive_duration: duration in minutes to automatically archive the thread after recent activity, can be set to: 60, 1440, 4320, 10080
            thread_type: The type of thread, defaults to public. ignored if creating thread from a message
            invitable: Whether non-moderators can add other non-moderators to a thread; only available when creating a private thread
            rate_limit_per_user: The time users must wait between sending messages (0-21600)
            message_id: An optional message to create a thread from.
            reason: An optional reason for the audit log

        Returns:
            The created thread

        """
        payload = {
            "name": name,
            "auto_archive_duration": auto_archive_duration,
            "rate_limit_per_user": rate_limit_per_user,
        }
        if message_id:
            return await self.request(
                Route(
                    "POST",
                    "/channels/{channel_id}/messages/{message_id}/threads",
                    channel_id=channel_id,
                    message_id=message_id,
                ),
                payload=payload,
                reason=reason,
            )
        payload["type"] = thread_type or ChannelType.GUILD_PUBLIC_THREAD
        payload["invitable"] = invitable
        return await self.request(
            Route("POST", "/channels/{channel_id}/threads", channel_id=channel_id), payload=payload, reason=reason
        )

    async def create_forum_thread(
        self,
        channel_id: "Snowflake_Type",
        name: str,
        auto_archive_duration: int,
        message: dict | FormData,
        applied_tags: List[str] = None,
        rate_limit_per_user: Absent[int] = MISSING,
        files: Absent["UPLOADABLE_TYPE"] = MISSING,
        reason: Absent[str] = MISSING,
    ) -> dict:
        """
        Create a thread within a forum channel.

        Args:
            channel_id: The id of the forum channel
            name: The name of the thread
            auto_archive_duration: Time before the thread will be automatically archived. Note 3 day and 7 day archive durations require the server to be boosted.
            message: The message-content for the post/thread
            applied_tags: The tags to apply to the thread
            rate_limit_per_user: The time users must wait between sending messages
            files: The files to upload
            reason: The reason for creating this thread

        Returns:
            The created thread object
        """
        return await self.request(
            Route("POST", "/channels/{channel_id}/threads", channel_id=channel_id),
            payload={
                "name": name,
                "auto_archive_duration": auto_archive_duration,
                "rate_limit_per_user": rate_limit_per_user,
                "message": message,
                "applied_tags": applied_tags,
            },
            files=files,
            reason=reason,
        )
