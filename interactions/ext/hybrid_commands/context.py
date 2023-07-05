import datetime

from typing import TYPE_CHECKING, Any, Optional, Union, Iterable, Sequence
from typing_extensions import Self


from interactions import (
    BaseContext,
    Permissions,
    Message,
    SlashContext,
    Client,
    Typing,
    Embed,
    BaseComponent,
    UPLOADABLE_TYPE,
    Snowflake_Type,
    Sticker,
    AllowedMentions,
    MessageReference,
    MessageFlags,
    to_snowflake,
    Attachment,
    process_message_payload,
)
from interactions.client.mixins.send import SendMixin
from interactions.ext import prefixed_commands as prefixed

if TYPE_CHECKING:
    from .hybrid_slash import HybridSlashCommand

__all__ = ("HybridContext",)


class DeferTyping:
    def __init__(self, ctx: "HybridContext", ephermal: bool) -> None:
        self.ctx = ctx
        self.ephermal = ephermal

    async def __aenter__(self) -> None:
        await self.ctx.defer(ephemeral=self.ephermal)

    async def __aexit__(self, *_) -> None:
        pass


class HybridContext(BaseContext, SendMixin):
    prefix: str
    "The prefix used to invoke this command."

    app_permissions: Permissions
    """The permissions available to this context"""

    deferred: bool
    """Whether the context has been deferred."""
    responded: bool
    """Whether the context has been responded to."""
    ephemeral: bool
    """Whether the context response is ephemeral."""

    _command_name: str
    """The command name."""
    _message: Message | None

    args: list[Any]
    """The arguments passed to the command."""
    kwargs: dict[str, Any]
    """The keyword arguments passed to the command."""

    __attachment_index__: int

    _slash_ctx: SlashContext | None
    _prefixed_ctx: prefixed.PrefixedContext | None

    def __init__(self, client: Client):
        super().__init__(client)
        self.prefix = ""
        self.app_permissions = Permissions(0)
        self.deferred = False
        self.responded = False
        self.ephemeral = False
        self._command_name = ""
        self.args = []
        self.kwargs = {}
        self._message = None
        self.__attachment_index__ = 0
        self._slash_ctx = None
        self._prefixed_ctx = None

    @classmethod
    def from_dict(cls, client: Client, payload: dict) -> None:
        # this doesn't mean anything, so just implement it to make abc happy
        raise NotImplementedError

    @classmethod
    def from_slash_context(cls, ctx: SlashContext) -> Self:
        self = cls(ctx.client)
        self.guild_id = ctx.guild_id
        self.channel_id = ctx.channel_id
        self.author_id = ctx.author_id
        self.message_id = ctx.message_id
        self.prefix = "/"
        self.app_permissions = ctx.app_permissions
        self.deferred = ctx.deferred
        self.responded = ctx.responded
        self.ephemeral = ctx.ephemeral
        self._command_name = ctx._command_name
        self.args = ctx.args
        self.kwargs = ctx.kwargs
        self._slash_ctx = ctx
        return self

    @classmethod
    def from_prefixed_context(cls, ctx: prefixed.PrefixedContext) -> Self:
        # this is a "best guess" on what the permissions are
        # this may or may not be totally accurate
        if hasattr(ctx.channel, "permissions_for"):
            app_permissions = ctx.channel.permissions_for(ctx.guild.me)  # type: ignore
        elif ctx.channel.type in {10, 11, 12}:  # it's a thread
            app_permissions = ctx.channel.parent_channel.permissions_for(ctx.guild.me)  # type: ignore

        self = cls(ctx.client)
        self.guild_id = ctx.guild_id
        self.channel_id = ctx.channel_id
        self.author_id = ctx.author_id
        self.message_id = ctx.message_id
        self._message = ctx.message
        self.prefix = ctx.prefix
        self.app_permissions = app_permissions
        self._command_name = ctx.command.qualified_name
        self.args = ctx.args
        self._prefixed_ctx = ctx
        return self

    @property
    def inner_context(self) -> SlashContext | prefixed.PrefixedContext:
        """The inner context that this hybrid context is wrapping."""
        return self._slash_ctx or self._prefixed_ctx  # type: ignore

    @property
    def command(self) -> "HybridSlashCommand":
        return self.client._interaction_lookup[self._command_name]

    @property
    def expires_at(self) -> Optional[datetime.datetime]:
        """The time at which the interaction expires."""
        if not self._slash_ctx:
            return None

        if self.responded:
            return self._slash_ctx.id.created_at + datetime.timedelta(minutes=15)
        return self._slash_ctx.id.created_at + datetime.timedelta(seconds=3)

    @property
    def expired(self) -> bool:
        """Whether the interaction has expired."""
        return datetime.datetime.utcnow() > self.expires_at if self._slash_ctx else False

    @property
    def deferred_ephemeral(self) -> bool:
        """Whether the interaction has been deferred ephemerally."""
        return self.deferred and self.ephemeral

    @property
    def message(self) -> Message | None:
        """The message that invoked this context."""
        return self._message or self.client.cache.get_message(self.channel_id, self.message_id)

    @property
    def typing(self) -> Typing | DeferTyping:
        """A context manager to send a _typing/defer state to a given channel as long as long as the wrapped operation takes."""
        if self._slash_ctx:
            return DeferTyping(self._slash_ctx, self.ephemeral)
        return self.channel.typing

    async def defer(self, ephemeral: bool = False) -> None:
        """
        Either defers the response (if used in an interaction) or triggers a typing indicator for 10 seconds (if used for messages).

        Args:
            ephemeral: Should the response be ephemeral? Only applies to responses for interactions.

        """
        if self._slash_ctx:
            await self._slash_ctx.defer(ephemeral=ephemeral)
        else:
            await self.channel.trigger_typing()

        self.deferred = True

    async def reply(
        self,
        content: Optional[str] = None,
        embeds: Optional[
            Union[
                Iterable[Union[Embed, dict]],
                Union[Embed, dict],
            ]
        ] = None,
        embed: Optional[Union[Embed, dict]] = None,
        **kwargs,
    ) -> "Message":
        """
        Reply to this message, takes all the same attributes as `send`.

        For interactions, this functions the same as `send`.
        """
        kwargs = locals()
        kwargs.pop("self")
        extra_kwargs = kwargs.pop("kwargs")
        kwargs |= extra_kwargs

        if self._slash_ctx:
            result = await self.send(**kwargs)
        else:
            kwargs.pop("ephemeral", None)
            result = await self._prefixed_ctx.reply(**kwargs)

        self.responded = True
        return result

    async def _send_http_request(
        self,
        message_payload: dict,
        files: Iterable["UPLOADABLE_TYPE"] | None = None,
    ) -> dict:
        if self._slash_ctx:
            return await self._slash_ctx._send_http_request(message_payload, files)
        return await self._prefixed_ctx._send_http_request(message_payload, files)

    async def send(
        self,
        content: Optional[str] = None,
        *,
        embeds: Optional[
            Union[
                Iterable[Union["Embed", dict]],
                Union["Embed", dict],
            ]
        ] = None,
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
            Union[
                Iterable[Union["Sticker", "Snowflake_Type"]],
                "Sticker",
                "Snowflake_Type",
            ]
        ] = None,
        allowed_mentions: Optional[Union["AllowedMentions", dict]] = None,
        reply_to: Optional[Union["MessageReference", "Message", dict, "Snowflake_Type"]] = None,
        files: Optional[Union["UPLOADABLE_TYPE", Iterable["UPLOADABLE_TYPE"]]] = None,
        file: Optional["UPLOADABLE_TYPE"] = None,
        tts: bool = False,
        suppress_embeds: bool = False,
        silent: bool = False,
        flags: Optional[Union[int, "MessageFlags"]] = None,
        delete_after: Optional[float] = None,
        ephemeral: bool = False,
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
            silent: Should this message be sent without triggering a notification.
            flags: Message flags to apply.
            delete_after: Delete message after this many seconds.
            ephemeral: Should this message be sent as ephemeral (hidden) - only works with interactions

        Returns:
            New message object that was sent.
        """
        flags = MessageFlags(flags or 0)
        if ephemeral and self._slash_ctx:
            flags |= MessageFlags.EPHEMERAL
            self.ephemeral = True
        if suppress_embeds:
            flags |= MessageFlags.SUPPRESS_EMBEDS
        if silent:
            flags |= MessageFlags.SILENT

        return await super().send(
            content=content,
            embeds=embeds,
            embed=embed,
            components=components,
            stickers=stickers,
            allowed_mentions=allowed_mentions,
            reply_to=reply_to,
            files=files,
            file=file,
            tts=tts,
            flags=flags,
            delete_after=delete_after,
            pass_self_into_delete=bool(self._slash_ctx),
            **kwargs,
        )

    async def delete(self, message: "Snowflake_Type") -> None:
        """
        Delete a message sent in response to this context. Must be in the same channel as the context.

        Args:
            message: The message to delete
        """
        if self._slash_ctx:
            return await self._slash_ctx.delete(message)
        await self.client.http.delete_message(self.channel_id, to_snowflake(message))

    async def edit(
        self,
        message: "Snowflake_Type",
        *,
        content: Optional[str] = None,
        embeds: Optional[
            Union[
                Iterable[Union["Embed", dict]],
                Union["Embed", dict],
            ]
        ] = None,
        embed: Optional[Union["Embed", dict]] = None,
        components: Optional[
            Union[
                Iterable[Iterable[Union["BaseComponent", dict]]],
                Iterable[Union["BaseComponent", dict]],
                "BaseComponent",
                dict,
            ]
        ] = None,
        attachments: Optional[Sequence[Attachment | dict]] = None,
        allowed_mentions: Optional[Union["AllowedMentions", dict]] = None,
        files: Optional[Union["UPLOADABLE_TYPE", Iterable["UPLOADABLE_TYPE"]]] = None,
        file: Optional["UPLOADABLE_TYPE"] = None,
        tts: bool = False,
    ) -> "Message":
        if self._slash_ctx:
            return await self._slash_ctx.edit(
                message,
                content=content,
                embeds=embeds,
                embed=embed,
                components=components,
                attachments=attachments,
                allowed_mentions=allowed_mentions,
                files=files,
                file=file,
                tts=tts,
            )

        message_payload = process_message_payload(
            content=content,
            embeds=embeds or embed,
            components=components,
            allowed_mentions=allowed_mentions,
            attachments=attachments,
            tts=tts,
        )
        if file:
            files = [file, *files] if files else [file]

        message_data = await self.client.http.edit_message(
            message_payload, self.channel_id, to_snowflake(message), files=files
        )
        if message_data:
            return self.client.cache.place_message_data(message_data)
