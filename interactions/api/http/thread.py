from typing import TYPE_CHECKING, Dict, List, Optional

from aiohttp import MultipartWriter

from ...utils.missing import MISSING
from ..models.channel import Channel
from ..models.misc import File
from .request import _Request
from .route import Route

if TYPE_CHECKING:
    from ...api.cache import Cache

__all__ = ("ThreadRequest",)


class ThreadRequest:
    _req: _Request
    cache: "Cache"

    def __init__(self) -> None:
        pass

    async def join_thread(self, thread_id: int) -> None:
        """
        Have the bot user join a thread.

        :param thread_id: The thread to join.
        """
        return await self._req.request(Route("PUT", f"/channels/{thread_id}/thread-members/@me"))

    async def leave_thread(self, thread_id: int) -> None:
        """
        Have the bot user leave a thread.

        :param thread_id: The thread to leave.
        """
        return await self._req.request(Route("DELETE", f"/channels/{thread_id}/thread-members/@me"))

    async def add_member_to_thread(self, thread_id: int, user_id: int) -> None:
        """
        Add another user to a thread.

        :param thread_id: The ID of the thread
        :param user_id: The ID of the user to add
        """
        return await self._req.request(
            Route("PUT", f"/channels/{thread_id}/thread-members/{user_id}")
        )

    async def remove_member_from_thread(self, thread_id: int, user_id: int) -> None:
        """
        Remove another user from a thread.

        :param thread_id: The ID of the thread
        :param user_id: The ID of the user to remove
        """
        return await self._req.request(
            Route("DELETE", f"/channels/{thread_id}/thread-members/{user_id}")
        )

    async def get_member_from_thread(self, thread_id: int, user_id: int) -> dict:
        """
        Get a member from a thread.

        :param thread_id: The ID of the thread
        :param user_id: The ID of the user to find
        :return: A thread member object, if they're in the thread.
        """
        # Returns 404 if they don't
        return await self._req.request(
            Route("GET", f"/channels/{thread_id}/thread-members/{user_id}")
        )

    async def list_thread_members(self, thread_id: int) -> List[dict]:
        """
        Get a list of members in the thread.

        :param thread_id: the id of the thread
        :return: a list of thread member objects
        """
        return await self._req.request(Route("GET", f"/channels/{thread_id}/thread-members"))

    async def list_public_archived_threads(
        self, channel_id: int, limit: int = None, before: Optional[int] = None
    ) -> List[dict]:
        """
        Get a list of archived public threads in a given channel.

        :param channel_id: The channel to get threads from
        :param limit: Optional limit of threads to
        :param before: Get threads before this Thread snowflake ID
        :return: a list of threads
        """
        payload = {}
        if limit:
            payload["limit"] = limit
        if before:
            payload["before"] = before
        return await self._req.request(
            Route("GET", f"/channels/{channel_id}/threads/archived/public"), json=payload
        )

    async def list_private_archived_threads(
        self, channel_id: int, limit: int = None, before: Optional[int] = None
    ) -> List[dict]:
        """
        Get a list of archived private threads in a channel.

        :param channel_id: The channel to get threads from
        :param limit: Optional limit of threads to
        :param before: Get threads before this Thread snowflake ID
        :return: a list of threads
        """
        payload = {}
        if limit:
            payload["limit"] = limit
        if before:
            payload["before"] = before
        return await self._req.request(
            Route("GET", f"/channels/{channel_id}/threads/archived/private"), json=payload
        )

    async def list_joined_private_archived_threads(
        self, channel_id: int, limit: int = None, before: Optional[int] = None
    ) -> List[dict]:
        """
        Get a list of archived private threads in a channel that the bot has joined.

        :param channel_id: The channel to get threads from
        :param limit: Optional limit of threads to
        :param before: Get threads before this snowflake ID
        :return: a list of threads
        """
        payload = {}
        if limit:
            payload["limit"] = limit
        if before:
            payload["before"] = before
        return await self._req.request(
            Route("GET", f"/channels/{channel_id}/users/@me/threads/archived/private"), json=payload
        )

    async def list_active_threads(self, guild_id: int) -> Dict[str, List[dict]]:
        """
        List active threads within a guild.

        :param guild_id: the guild id to get threads from
        :return: A list of active threads
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/threads/active"))

    async def create_thread(
        self,
        channel_id: int,
        name: str,
        thread_type: int = None,
        auto_archive_duration: Optional[int] = None,
        invitable: Optional[bool] = None,
        message_id: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> dict:
        """
        From a given channel, create a Thread with an optional message to start with.

        :param channel_id: The ID of the channel to create this thread in
        :param name: The name of the thread
        :param auto_archive_duration: duration in minutes to automatically archive the thread after recent activity,
            can be set to: 60, 1440, 4320, 10080
        :param thread_type: The type of thread, defaults to public. ignored if creating thread from a message
        :param invitable: Boolean to display if the Thread is open to join or private.
        :param message_id: An optional message to create a thread from.
        :param reason: An optional reason for the audit log
        :return: The created thread
        """
        payload = {"name": name}
        if auto_archive_duration:
            payload["auto_archive_duration"] = auto_archive_duration
        if message_id:
            request = await self._req.request(
                Route("POST", f"/channels/{channel_id}/messages/{message_id}/threads"),
                json=payload,
                reason=reason,
            )
            if request.get("id"):
                self.cache[Channel].add(Channel(**request))
                return request

        payload["type"] = thread_type
        payload["invitable"] = invitable
        request = await self._req.request(
            Route("POST", f"/channels/{channel_id}/threads"), json=payload, reason=reason
        )
        if request.get("id"):
            self.cache[Channel].add(Channel(**request))

        return request

    async def create_thread_in_forum(
        self,
        channel_id: int,
        name: str,
        auto_archive_duration: int,
        message: dict,
        applied_tags: List[str] = None,
        files: Optional[List[File]] = MISSING,
        rate_limit_per_user: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> dict:
        """
        From a given Forum channel, create a Thread with a message to start with.

        :param channel_id: The ID of the channel to create this thread in
        :param name: The name of the thread
        :param auto_archive_duration: duration in minutes to automatically archive the thread after recent activity,
            can be set to: 60, 1440, 4320, 10080
        :param message: The payload/dictionary contents of the first message in the forum thread.
        :param applied_tags: List of tag ids that can be applied to the forum, if any.
        :param files: An optional list of files to send attached to the message.
        :param rate_limit_per_user: Seconds a user has to wait before sending another message (0 to 21600), if given.
        :param reason: An optional reason for the audit log
        :return: Returns a Thread in a Forum object with a starting Message.
        """
        query = {"use_nested_fields": 1}

        payload = {"name": name, "auto_archive_duration": auto_archive_duration, "message": message}
        if rate_limit_per_user:
            payload["rate_limit_per_user"] = rate_limit_per_user
        if applied_tags:
            payload["applied_tags"] = applied_tags

        data = None
        if files is not MISSING and files and len(files) > 0:  # edge case `None`
            data = MultipartWriter("form-data")
            part = data.append_json(payload)
            part.set_content_disposition("form-data", name="payload_json")
            payload = None

            for id, file in enumerate(files):
                part = data.append(
                    file._fp,
                )
                part.set_content_disposition(
                    "form-data", name=f"files[{str(id)}]", filename=file._filename
                )
        else:
            payload.update(message)

        return await self._req.request(
            Route("POST", f"/channels/{channel_id}/threads"),
            json=payload,
            data=data,
            params=query,
            reason=reason,
        )
