from typing import TYPE_CHECKING, Any, Iterable, Optional, Union

import interactions.models as models

if TYPE_CHECKING:
    from interactions.client import Client
    from interactions.models.discord.file import UPLOADABLE_TYPE
    from interactions.models.discord.components import BaseComponent
    from interactions.models.discord.embed import Embed
    from interactions.models.discord.message import AllowedMentions, Message, MessageReference
    from interactions.models.discord.sticker import Sticker
    from interactions.models.discord.snowflake import Snowflake_Type
    from interactions.models.discord.enums import MessageFlags

__all__ = ("SendMixin",)


class SendMixin:
    client: "Client"

    async def _send_http_request(
        self, message_payload: dict, files: Iterable["UPLOADABLE_TYPE"] | None = None
    ) -> dict:
        raise NotImplementedError

    async def send(
        self,
        content: Optional[str] = None,
        *,
        embeds: Optional[Union[Iterable[Union["Embed", dict]], Union["Embed", dict]]] = None,
        embed: Optional[Union["Embed", dict]] = None,
        components: Optional[
            Union[
                Iterable[Iterable[Union["BaseComponent", dict]]],
                Iterable[Union["BaseComponent", dict]],
                "BaseComponent",
                dict,
            ]
        ] = None,
        stickers: Optional[
            Union[Iterable[Union["Sticker", "Snowflake_Type"]], "Sticker", "Snowflake_Type"]
        ] = None,
        allowed_mentions: Optional[Union["AllowedMentions", dict]] = None,
        reply_to: Optional[Union["MessageReference", "Message", dict, "Snowflake_Type"]] = None,
        files: Optional[Union["UPLOADABLE_TYPE", Iterable["UPLOADABLE_TYPE"]]] = None,
        file: Optional["UPLOADABLE_TYPE"] = None,
        tts: bool = False,
        suppress_embeds: bool = False,
        flags: Optional[Union[int, "MessageFlags"]] = None,
        delete_after: Optional[float] = None,
        **kwargs: Any,
    ) -> "Message":
        """
        Send a message.

        Args:
            content: Message text content.
            embeds: Embedded rich content (up to 6000 characters).
            embed: Embedded rich content (up to 6000 characters).
            components: The components to include with the message.
            stickers: IDs of up to 3 stickers in the server to send in the message.
            allowed_mentions: Allowed mentions for the message.
            reply_to: Message to reference, must be from the same channel.
            files: Files to send, the path, bytes or File() instance, defaults to None. You may have up to 10 files.
            file: Files to send, the path, bytes or File() instance, defaults to None. You may have up to 10 files.
            tts: Should this message use Text To Speech.
            suppress_embeds: Should embeds be suppressed on this send
            flags: Message flags to apply.
            delete_after: Delete message after this many seconds.

        Returns:
            New message object that was sent.

        """
        if suppress_embeds:
            if isinstance(flags, int):
                flags = MessageFlags(flags)
            flags = flags | MessageFlags.SUPPRESS_EMBEDS

        message_payload = models.discord.message.process_message_payload(
            content=content,
            embeds=embeds or embed,
            components=components,
            stickers=stickers,
            allowed_mentions=allowed_mentions,
            reply_to=reply_to,
            tts=tts,
            flags=flags,
            **kwargs,
        )

        message_data = await self._send_http_request(message_payload, files=files or file)
        if message_data:
            message = self.client.cache.place_message_data(message_data)
            if delete_after:
                await message.delete(delay=delete_after)
            return message
        
    async def respond(
        self,
        content: Optional[str] = None,
        *,
        embeds: Optional[Union[Iterable[Union["Embed", dict]], Union["Embed", dict]]] = None,
        embed: Optional[Union["Embed", dict]] = None,
        components: Optional[
            Union[
                Iterable[Iterable[Union["BaseComponent", dict]]],
                Iterable[Union["BaseComponent", dict]],
                "BaseComponent",
                dict,
            ]
        ] = None,
        stickers: Optional[
            Union[Iterable[Union["Sticker", "Snowflake_Type"]], "Sticker", "Snowflake_Type"]
        ] = None,
        allowed_mentions: Optional[Union["AllowedMentions", dict]] = None,
        reply_to: Optional[Union["MessageReference", "Message", dict, "Snowflake_Type"]] = None,
        files: Optional[Union["UPLOADABLE_TYPE", Iterable["UPLOADABLE_TYPE"]]] = None,
        file: Optional["UPLOADABLE_TYPE"] = None,
        tts: bool = False,
        suppress_embeds: bool = False,
        flags: Optional[Union[int, "MessageFlags"]] = None,
        delete_after: Optional[float] = None,
        **kwargs: Any,
    ) -> "Message":
        """An alias of the send method for messages."""
        return await self.send(
            content,
            embeds=embeds,
            embed=embed,
            components=components,
            stickers=stickers,
            allowed_mentions=allowed_mentions,
            reply_to=reply_to,
            files=files,
            file=file,
            tts=tts,
            suppress_embeds=suppress_embeds,
            flags=flags,
            delete_after=delete_after,
            **kwargs
        )
