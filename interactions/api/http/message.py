from typing import TYPE_CHECKING, List, Optional, Union

from aiohttp import MultipartWriter

from ...utils.missing import MISSING
from ..models.message import Embed, Message, Sticker
from ..models.misc import AllowedMentions, File, Snowflake
from .request import _Request
from .route import Route

if TYPE_CHECKING:
    from ...api.cache import Cache

__all__ = ("MessageRequest",)


class MessageRequest:
    _req: _Request
    cache: "Cache"

    def __init__(self) -> None:
        pass

    async def send_message(
        self,
        channel_id: Union[int, Snowflake],
        content: str,
        tts: bool = False,
        embeds: Optional[List[Embed]] = None,
        nonce: Union[int, str] = None,
        allowed_mentions: Optional[Union[AllowedMentions, dict]] = None,
        message_reference: Optional[Message] = None,
        stickers: Optional[List[Sticker]] = None,
    ) -> dict:
        """
        A higher level implementation of :meth:`create_message()` that handles the payload dict internally.
        Does not integrate components into the function, and is a port from v3.0.0
        """
        payload = {}

        if content:
            payload["content"] = content

        if tts:
            payload["tts"] = True

        if embeds:
            payload["embeds"] = embeds

        if nonce:
            payload["nonce"] = nonce

        if allowed_mentions:
            payload["allowed_mentions"] = (
                allowed_mentions._json
                if isinstance(allowed_mentions, AllowedMentions)
                else allowed_mentions
            )

        if message_reference:
            payload["message_reference"] = message_reference

        if stickers:
            payload["sticker_ids"] = [str(sticker.id) for sticker in stickers]

        # TODO: post-v4. add attachments to payload.

        if isinstance(channel_id, Snowflake):
            channel_id = int(channel_id)

        return await self.create_message(payload, channel_id)

    async def create_message(
        self, payload: dict, channel_id: int, files: Optional[List[File]] = MISSING
    ) -> dict:
        """
        Send a message to the specified channel.

        :param payload: Dictionary contents of a message. (i.e. message payload)
        :param channel_id: Channel snowflake ID.
        :param files: An optional list of files to send attached to the message.
        :return dict: Dictionary representing a message (?)
        """

        data = None
        if files is not MISSING and len(files) > 0:
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

        request = await self._req.request(
            Route("POST", "/channels/{channel_id}/messages", channel_id=channel_id),
            json=payload,
            data=data,
        )
        if request.get("id"):
            self.cache[Message].add(Message(**request, _client=self))

        return request

    async def get_message(self, channel_id: int, message_id: int) -> Optional[dict]:
        """
        Get a specific message in the channel.

        :param channel_id: the channel this message belongs to
        :param message_id: the id of the message
        :return: message if it exists.
        """
        res = await self._req.request(Route("GET", f"/channels/{channel_id}/messages/{message_id}"))

        self.cache[Message].merge(Message(**res, _client=self))

        return res

    async def delete_message(
        self, channel_id: int, message_id: int, reason: Optional[str] = None
    ) -> None:
        """
        Deletes a message from a specified channel.

        :param channel_id: Channel snowflake ID.
        :param message_id: Message snowflake ID.
        :param reason: Optional reason to show up in the audit log. Defaults to `None`.
        """
        r = Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}",
            channel_id=channel_id,
            message_id=message_id,
        )
        return await self._req.request(r, reason=reason)

    async def delete_messages(
        self, channel_id: int, message_ids: List[int], reason: Optional[str] = None
    ) -> None:
        """
        Deletes messages from a specified channel.

        :param channel_id: Channel snowflake ID.
        :param message_ids: An array of message snowflake IDs.
        :param reason: Optional reason to show up in the audit log. Defaults to `None`.
        """
        r = Route("POST", "/channels/{channel_id}/messages/bulk-delete", channel_id=channel_id)
        payload = {
            "messages": message_ids,
        }

        return await self._req.request(r, json=payload, reason=reason)

    async def edit_message(
        self, channel_id: int, message_id: int, payload: dict, files: Optional[List[File]] = MISSING
    ) -> dict:
        """
        Edits a message that already exists.

        :param channel_id: Channel snowflake ID.
        :param message_id: Message snowflake ID.
        :param payload: Any new data that needs to be changed.
        :param files: An optional list of files to send attached to the message.
        :type payload: dict
        :return: A message object with edited attributes.
        """
        data = None
        if files is not MISSING and len(files) > 0:
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

        return await self._req.request(
            Route(
                "PATCH",
                "/channels/{channel_id}/messages/{message_id}",
                channel_id=channel_id,
                message_id=message_id,
            ),
            json=payload,
            data=data,
        )

    async def pin_message(self, channel_id: int, message_id: int) -> None:
        """
        Pin a message to a channel.

        :param channel_id: Channel ID snowflake.
        :param message_id: Message ID snowflake.
        """
        return await self._req.request(Route("PUT", f"/channels/{channel_id}/pins/{message_id}"))

    async def unpin_message(self, channel_id: int, message_id: int) -> None:
        """
        Unpin a message to a channel.

        :param channel_id: Channel ID snowflake.
        :param message_id: Message ID snowflake.
        """
        return await self._req.request(Route("DELETE", f"/channels/{channel_id}/pins/{message_id}"))

    async def publish_message(self, channel_id: int, message_id: int) -> dict:
        """
        Publishes (API calls it crossposts) a message in a News channel to any that is followed by.

        :param channel_id: Channel the message is in
        :param message_id: The id of the message to publish
        :return: message object
        """
        return await self._req.request(
            Route("POST", f"/channels/{channel_id}/messages/{message_id}/crosspost")
        )
