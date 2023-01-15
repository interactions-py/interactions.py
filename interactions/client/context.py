import asyncio
from datetime import datetime
from logging import Logger
from typing import TYPE_CHECKING, List, Optional, Tuple, Union

from ..api.error import LibraryException
from ..api.models.channel import Channel, Thread
from ..api.models.flags import MessageFlags, Permissions
from ..api.models.guild import Guild
from ..api.models.member import Member
from ..api.models.message import Attachment, Embed, File, Message, MessageReference
from ..api.models.misc import AllowedMentions, Snowflake
from ..api.models.user import User
from ..base import get_logger
from ..utils.attrs_utils import ClientSerializerMixin, convert_int, define, field
from ..utils.missing import MISSING
from .enums import ComponentType, InteractionCallbackType, InteractionType, Locale
from .models.command import Choice
from .models.component import ActionRow, Button, Modal, SelectMenu, _build_components
from .models.misc import InteractionData

if TYPE_CHECKING:
    from .bot import Client, Extension
    from .models.command import Command

log: Logger = get_logger("context")

__all__ = (
    "_Context",
    "CommandContext",
    "ComponentContext",
)


@define()
class _Context(ClientSerializerMixin):
    """
    The base class of "context" for dispatched event data
    from the gateway. The premise of having this class is so
    that the user-facing API is able to allow developers to
    easily access information presented from any event in
    a "contextualized" sense.
    """

    message: Optional[Message] = field(converter=Message, default=None, add_client=True)
    member: Optional[Member] = field(default=None, converter=Member, add_client=True)
    user: User = field(converter=User, default=None, add_client=True)
    id: Snowflake = field(converter=Snowflake)
    application_id: Snowflake = field(converter=Snowflake)
    type: InteractionType = field(converter=InteractionType)
    callback: Optional[InteractionCallbackType] = field(
        converter=InteractionCallbackType, default=None
    )
    data: InteractionData = field(converter=InteractionData)
    version: int = field()
    token: str = field()
    guild_id: Snowflake = field(converter=Snowflake)
    channel_id: Snowflake = field(converter=Snowflake)
    responded: bool = field(default=False)
    deferred: bool = field(default=False)
    app_permissions: Permissions = field(converter=convert_int(Permissions), default=None)
    locale: Optional[Locale] = field(converter=Locale, default=None)
    guild_locale: Optional[Locale] = field(converter=Locale, default=None)

    def __attrs_post_init__(self) -> None:
        if self.member and self.guild_id:
            self.member._extras["guild_id"] = self.guild_id

        if self.user is None:
            self.user = self.member.user if self.member else None

        if self.member and not self.member.user and self.user:
            self.member.user = self.user

    @property
    def deferred_ephemeral(self) -> bool:
        """
        .. versionadded:: 4.4.0

        Returns whether the current interaction was deferred ephemerally.
        """
        return bool(
            self.message.flags & MessageFlags.EPHEMERAL
            and self.message.flags & MessageFlags.LOADING
        )

    @property
    def created_at(self) -> datetime:
        """
        .. versionadded:: 4.4.0

        Returns when the interaction was created.
        """
        return self.id.timestamp

    @property
    def author(self) -> Optional[Member]:
        """
        Returns the author/member that invoked the interaction.
        """
        return self.member

    @property
    def channel(self) -> Optional[Channel]:
        """
        .. versionadded:: 4.1.0

        .. versionchanged:: 4.4.0
            Channel now returns ``None`` instead of ``MISSING`` if it is not found to avoid confusion

        Returns the current channel, if cached.
        """
        return self._client.cache[Channel].get(self.channel_id, None) or self._client.cache[
            Thread
        ].get(self.channel_id, None)

    @property
    def guild(self) -> Optional[Guild]:
        """
         .. versionadded:: 4.1.0

         .. versionchanged:: 4.4.0
            Guild now returns ``None`` instead of ``MISSING`` if it is not found to avoid confusion

        Returns the current guild, if cached.
        """

        return self._client.cache[Guild].get(self.guild_id, None)

    async def get_channel(self) -> Channel:
        """
        .. versionadded:: 4.1.0

        This gets the channel the context was invoked in. If the channel is not cached, an HTTP request is made.

        :return: The channel as object
        :rtype: Channel
        """
        if channel := self.channel:
            await asyncio.sleep(0)
            return channel

        res = await self._client.get_channel(int(self.channel_id))
        return Channel(**res, _client=self._client)

    async def get_guild(self) -> Guild:
        """
        .. versionadded:: 4.1.0

        This gets the guild the context was invoked in. If the guild is not cached, an HTTP request is made.

        :return: The guild as object
        :rtype: Guild
        """

        if guild := self.guild:
            await asyncio.sleep(0)
            return guild

        res = await self._client.get_guild(int(self.guild_id))
        return Guild(**res, _client=self._client)

    async def send(
        self,
        content: Optional[str] = MISSING,
        *,
        tts: Optional[bool] = MISSING,
        attachments: Optional[List[Attachment]] = MISSING,
        files: Optional[Union[File, List[File]]] = MISSING,
        embeds: Optional[Union[Embed, List[Embed]]] = MISSING,
        allowed_mentions: Optional[Union[AllowedMentions, dict]] = MISSING,
        components: Optional[
            Union[ActionRow, Button, SelectMenu, List[ActionRow], List[Button], List[SelectMenu]]
        ] = MISSING,
        ephemeral: Optional[bool] = False,
        suppress_embeds: bool = False,
    ) -> Tuple[dict, List[File]]:
        """
        This allows the invocation state described in the "context"
        to send an interaction response.

        :param Optional[str] content: The contents of the message as a string or string-converted value.
        :param Optional[bool] tts: Whether the message utilizes the text-to-speech Discord programme or not.
        :param Optional[List[Attachment]] attachments: The attachments to attach to the message. Needs to be uploaded to the CDN first
        :param Optional[Union[File, List[File]]] files:
            .. versionadded:: 4.4.0

            The files to attach to the message.
        :param Optional[Union[Embed, List[Embed]]] embeds: An embed, or list of embeds for the message.
        :param Optional[Union[AllowedMentions, dict]] allowed_mentions: The allowed mentions for the message.
        :param Optional[Union[ActionRow, Button, SelectMenu, List[Union[ActionRow, Button, SelectMenu]]]] components: A component, or list of components for the message.
        :param Optional[bool] ephemeral: Whether the response is hidden or not.
        :param Optional[bool] suppress_embeds: Whether embeds are not shown in the message.
        :return: The sent message.
        """
        if (
            content is MISSING
            and self.message
            and self.callback == InteractionCallbackType.DEFERRED_UPDATE_MESSAGE
        ):
            _content = self.message.content
        else:
            _content: str = "" if content is MISSING else content
        _tts: bool = False if tts is MISSING else tts

        if (
            embeds is MISSING
            and self.message
            and self.callback == InteractionCallbackType.DEFERRED_UPDATE_MESSAGE
        ):
            embeds = self.message.embeds
        _embeds: list = (
            []
            if not embeds or embeds is MISSING
            else ([embed._json for embed in embeds] if isinstance(embeds, list) else [embeds._json])
        )
        _allowed_mentions: dict = (
            {}
            if allowed_mentions is MISSING
            else allowed_mentions._json
            if isinstance(allowed_mentions, AllowedMentions)
            else allowed_mentions
        )

        if components is not MISSING and components:
            # components could be not missing but an empty list

            _components = _build_components(components=components)
        elif (
            components is MISSING
            and self.message
            and self.callback == InteractionCallbackType.DEFERRED_UPDATE_MESSAGE
        ):

            if isinstance(self.message.components, list):
                _components = self.message.components
            else:
                _components = [self.message.components]

        else:
            _components = []

        _flags = MessageFlags.EPHEMERAL if ephemeral else MessageFlags(0)
        if suppress_embeds:
            _flags |= MessageFlags.SUPPRESS_EMBEDS

        _attachments = [] if attachments is MISSING else [a._json for a in attachments]

        if not files or files is MISSING:
            _files = []
        elif isinstance(files, list):
            _files = [file._json_payload(id) for id, file in enumerate(files)]
        else:
            _files = [files._json_payload(0)]
            files = [files]

        _files.extend(_attachments)

        return (
            dict(
                content=_content,
                tts=_tts,
                embeds=_embeds,
                allowed_mentions=_allowed_mentions,
                components=_components,
                attachments=_files,
                flags=_flags.value,
            ),
            files,
        )

    async def edit(
        self,
        content: Optional[str] = MISSING,
        *,
        tts: Optional[bool] = MISSING,
        attachments: Optional[List[Attachment]] = MISSING,
        files: Optional[Union[File, List[File]]] = MISSING,
        embeds: Optional[Union[Embed, List[Embed]]] = MISSING,
        allowed_mentions: Optional[Union[AllowedMentions, dict]] = MISSING,
        message_reference: Optional[MessageReference] = MISSING,
        components: Optional[
            Union[ActionRow, Button, SelectMenu, List[ActionRow], List[Button], List[SelectMenu]]
        ] = MISSING,
    ) -> Tuple[dict, List[File]]:  # sourcery skip: low-code-quality
        """
        This allows the invocation state described in the "context"
        to send an interaction response.

        :param Optional[str] content: The contents of the message as a string or string-converted value.
        :param Optional[bool] tts: Whether the message utilizes the text-to-speech Discord programme or not.
        :param Optional[List[Attachment]] attachments: The attachments to attach to the message. Needs to be uploaded to the CDN first
        :param Optional[Union[File, List[File]]] files:
            .. versionadded:: 4.4.0

            The files to attach to the message.
        :param Optional[Union[Embed, List[Embed]]] embeds: An embed, or list of embeds for the message.
        :param Optional[Union[AllowedMentions, dict]] allowed_mentions: The allowed mentions for the message.
        :param Optional[MessageReference] message_reference: Include to make your message a reply.
        :param Optional[Union[ActionRow, Button, SelectMenu, List[Union[ActionRow, Button, SelectMenu]]]] components: A component, or list of components for the message.
        :return: The edited message.
        """

        payload = {}

        if self.message.content is not None or content is not MISSING:
            _content: str = self.message.content if content is MISSING else content
            payload["content"] = _content

        _tts: bool = False if tts is MISSING else tts
        payload["tts"] = _tts

        if self.message.embeds is not None or embeds is not MISSING:
            if embeds is MISSING:
                embeds = self.message.embeds
            _embeds: list = (
                ([embed._json for embed in embeds] if isinstance(embeds, list) else [embeds._json])
                if embeds
                else []
            )

            payload["embeds"] = _embeds

        if self.message.attachments is not None or attachments is not MISSING:
            if attachments is MISSING:
                attachments = self.message.attachments
            _attachments: list = (
                (
                    [attachment._json for attachment in attachments]
                    if isinstance(attachments, list)
                    else [attachments._json]
                )
                if attachments
                else []
            )

        if not files or files is MISSING:
            _files = []
        elif isinstance(files, list):
            _files = [file._json_payload(id) for id, file in enumerate(files)]
        else:
            _files = [files._json_payload(0)]
            files = [files]

        _files.extend(_attachments)

        payload["attachments"] = _files

        _allowed_mentions: dict = (
            {}
            if allowed_mentions is MISSING
            else allowed_mentions._json
            if isinstance(allowed_mentions, AllowedMentions)
            else allowed_mentions
        )
        _message_reference: dict = {} if message_reference is MISSING else message_reference._json

        payload["allowed_mentions"] = _allowed_mentions
        payload["message_reference"] = _message_reference

        if self.message.components is not None or components is not MISSING:
            if components is MISSING:
                _components = _build_components(components=self.message.components)
            elif not components:
                _components = []
            else:
                _components = _build_components(components=components)

            payload["components"] = _components

        return payload, files

    async def popup(self, modal: Modal) -> dict:
        """
        This "pops up" a modal to present information back to the
        user.

        :param Modal modal: The components you wish to show.
        """

        payload: dict = {
            "type": InteractionCallbackType.MODAL.value,
            "data": {
                "title": modal.title,
                "components": modal._json.get("components"),
                "custom_id": modal.custom_id,
            },
        }

        await self._client.create_interaction_response(
            token=self.token,
            application_id=int(self.id),
            data=payload,
        )
        self.responded = True

        return payload

    async def has_permissions(
        self, *permissions: Union[int, Permissions], operator: str = "and"
    ) -> bool:
        r"""
        .. versionadded:: 4.3.2

        Returns whether the author of the interaction has the permissions in the given context.

        :param Union[int, Permissions] \*permissions: The list of permissions
        :param Optional[str] operator: The operator to use to calculate permissions. Possible values: ``and``, ``or``. Defaults to ``and``.
        :return: Whether the author has the permissions
        :rtype: bool
        """
        if operator == "and":
            return all(perm in self.author.permissions for perm in permissions)
        else:
            return any(perm in self.author.permissions for perm in permissions)


@define()
class CommandContext(_Context):
    """
    A derivation of context
    designed specifically for application command data.

    :ivar Snowflake id: The ID of the interaction.
    :ivar Snowflake application_id: The application ID of the interaction.
    :ivar InteractionType type: The type of interaction.
    :ivar InteractionData data: The application command data.
    :ivar Optional[Union[Message, Member, User]] target: The target selected if this interaction is invoked as a context menu.
    :ivar str token: The token of the interaction response.
    :ivar Snowflake guild_id: The ID of the current guild.
    :ivar Snowflake channel_id: The ID of the current channel.
    :ivar User user: The user data model.
    :ivar bool responded: Whether an original response was made or not.
    :ivar bool deferred: Whether the response was deferred or not.
    :ivar Optional[Locale] locale: The selected language of the user invoking the interaction.
    :ivar Optional[Locale] guild_locale: The guild's preferred language, if invoked in a guild.
    :ivar Permissions app_permissions: Bitwise set of permissions the bot has within the channel the interaction was sent from.
    :ivar Client client:
        .. versionadded:: 4.3.0

        The client instance that the command belongs to.
    :ivar Command command:
        .. versionadded:: 4.3.0

        The command object that is being invoked.
    :ivar Extension extension:
        .. versionadded:: 4.3.0

        The extension the command belongs to.
    """

    target: Optional[Union[Message, Member, User]] = field(default=None)

    client: "Client" = field(default=None, init=False)
    command: "Command" = field(default=None, init=False)
    extension: "Extension" = field(default=None, init=False)

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()

        if self.data.target_id:
            target = self.data.target_id

            if self.data.type == 2:
                self.target = (
                    self.data.resolved.members[target]
                    if self.guild_id and str(self.data.target_id) in self.data.resolved.members
                    else self.data.resolved.users[target]
                )
                # member id would have potential to exist, and therefore have target def priority.

            elif self.data.type == 3:
                self.target = self.data.resolved.messages[target]

            self.target._client = self._client

    async def edit(
        self, content: Optional[str] = MISSING, **kwargs
    ) -> Message:  # sourcery skip: low-code-quality

        payload, files = await super().edit(content, **kwargs)
        msg = None

        if self.deferred:
            if (
                hasattr(self.message, "id")
                and self.message.id is not None
                and self.message.flags != 64
            ):
                try:
                    res = await self._client.edit_message(
                        int(self.channel_id), int(self.message.id), payload=payload, files=files
                    )
                except LibraryException as e:
                    if e.code in {10015, 10018}:
                        log.warning(f"You can't edit hidden messages." f"({e.message}).")
                    else:
                        # if its not ephemeral or some other thing.
                        raise e from e
                else:
                    self.message = msg = Message(**res, _client=self._client)
            else:
                try:
                    res = await self._client.edit_interaction_response(
                        token=self.token,
                        application_id=str(self.application_id),
                        data=payload,
                        files=files,
                        message_id=self.message.id
                        if self.message and self.message.flags != 64
                        else "@original",
                    )
                except LibraryException as e:
                    if e.code in {10015, 10018}:
                        log.warning(f"You can't edit hidden messages." f"({e.message}).")
                    else:
                        # if its not ephemeral or some other thing.
                        raise e from e
                else:
                    self.message = msg = Message(**res, _client=self._client)
        else:
            try:
                res = await self._client.edit_interaction_response(
                    token=self.token,
                    application_id=str(self.application_id),
                    data=payload,
                    files=files,
                )
            except LibraryException as e:
                if e.code in {10015, 10018}:
                    log.warning(f"You can't edit hidden messages." f"({e.message}).")
                else:
                    # if its not ephemeral or some other thing.
                    raise e from e
            else:
                self.message = msg = Message(**res, _client=self._client)

        return msg if msg is not None else Message(**payload, _client=self._client)

    async def defer(self, ephemeral: Optional[bool] = False) -> Message:
        """
        .. versionchanged:: 4.4.0
            Now returns the created message object

        This "defers" an interaction response, allowing up
        to a 15-minute delay between invocation and responding.

        :param Optional[bool] ephemeral: Whether the deferred state is hidden or not.
        :return: The deferred message
        :rtype: Message
        """
        if not self.responded:
            self.deferred = True
            _ephemeral: int = MessageFlags.EPHEMERAL.value if ephemeral else 0
            self.callback = InteractionCallbackType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE
            await self._client.create_interaction_response(
                token=self.token,
                application_id=int(self.id),
                data={"type": self.callback.value, "data": {"flags": _ephemeral}},
            )
            try:
                _msg = await self._client.get_original_interaction_response(
                    self.token, str(self.application_id)
                )
            except LibraryException:
                pass
            else:
                self.message = Message(**_msg, _client=self._client)
            self.responded = True
            return self.message

    async def send(self, content: Optional[str] = MISSING, **kwargs) -> Message:
        payload, files = await super().send(content, **kwargs)

        if not self.deferred:
            self.callback = InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE

        _payload: dict = {"type": self.callback.value, "data": payload}

        msg = None
        if self.responded:
            res = await self._client._post_followup(
                data=payload,
                files=files,
                token=self.token,
                application_id=str(self.application_id),
            )
            self.message = msg = Message(**res, _client=self._client)
        else:
            await self._client.create_interaction_response(
                token=self.token,
                application_id=int(self.id),
                data=_payload,
                files=files,
            )

            try:
                _msg = await self._client.get_original_interaction_response(
                    self.token, str(self.application_id)
                )
            except LibraryException:
                pass
            else:
                self.message = msg = Message(**_msg, _client=self._client)

            self.responded = True

        if msg is not None:
            return msg
        return Message(
            **payload,
            _client=self._client,
            author={"_client": self._client, "id": None, "username": None, "discriminator": None},
        )

    async def delete(self) -> None:
        """
        This deletes the interaction response of a message sent by
        the contextually derived information from this class.

        .. note::
            Doing this will proceed in the context message no longer
            being present.
        """
        if self.responded and self.message is not None:
            await self._client.delete_interaction_response(
                application_id=str(self.application_id),
                token=self.token,
                message_id=int(self.message.id),
            )
        else:
            await self._client.delete_interaction_response(
                application_id=str(self.application_id), token=self.token
            )

        self.message = None

    async def populate(self, choices: Union[Choice, List[Choice]]) -> List[Choice]:
        """
        This "populates" the list of choices that the client-end
        user will be able to select from in the autocomplete field.

        .. warning::
            Only a maximum of ``25`` choices may be presented
            within an autocomplete option.

        :param Union[Choice, List[Choice]] choices: The choices you wish to present.
        :return: The list of choices you've given.
        :rtype: List[Choice]
        """

        _choices: Union[list, None] = []

        if not choices or (isinstance(choices, list) and len(choices) == 0):
            _choices = None
        elif isinstance(choices, Choice):
            _choices.append(choices._json)
        elif isinstance(choices, list) and all(isinstance(choice, Choice) for choice in choices):
            _choices = [choice._json for choice in choices]
        elif all(
            isinstance(choice, dict) and all(isinstance(x, str) for x in choice)
            for choice in choices
        ):
            _choices = list(choices)
        else:
            raise LibraryException(6, message="Autocomplete choice items must be of type Choice")

        await self._client.create_interaction_response(
            token=self.token,
            application_id=int(self.id),
            data={
                "type": InteractionCallbackType.APPLICATION_COMMAND_AUTOCOMPLETE_RESULT.value,
                "data": {"choices": _choices},
            },
        )

        return _choices


@define()
class ComponentContext(_Context):
    """
    A derivation of context
    designed specifically for component data.

    :ivar Snowflake id: The ID of the interaction.
    :ivar Snowflake application_id: The application ID of the interaction.
    :ivar InteractionType type: The type of interaction.
    :ivar InteractionData data: The application command data.
    :ivar str token: The token of the interaction response.
    :ivar Snowflake guild_id: The ID of the current guild.
    :ivar Snowflake channel_id: The ID of the current channel.
    :ivar Optional[Message] message: The message data model.
    :ivar User user: The user data model.
    :ivar bool responded: Whether an original response was made or not.
    :ivar bool deferred: Whether the response was deferred or not.
    :ivar Optional[Locale] locale: The selected language of the user invoking the interaction.
    :ivar Optional[Locale] guild_locale: The guild's preferred language, if invoked in a guild.
    :ivar Permissions app_permissions: Bitwise set of permissions the bot has within the channel the interaction was sent from.
    """

    async def edit(self, content: Optional[str] = MISSING, **kwargs) -> Message:
        payload, files = await super().edit(content, **kwargs)
        msg = None

        if not self.deferred:
            self.callback = InteractionCallbackType.UPDATE_MESSAGE
            await self._client.create_interaction_response(
                data={"type": self.callback.value, "data": payload},
                files=files,
                token=self.token,
                application_id=int(self.id),
            )

            try:
                _msg = await self._client.get_original_interaction_response(
                    self.token, str(self.application_id)
                )
            except LibraryException:
                pass
            else:
                self.message = msg = Message(**_msg, _client=self._client)

            self.responded = True
        elif self.callback != InteractionCallbackType.DEFERRED_UPDATE_MESSAGE:
            await self._client._post_followup(
                data=payload,
                files=files,
                token=self.token,
                application_id=str(self.application_id),
            )
        else:
            res = await self._client.edit_interaction_response(
                data=payload,
                files=files,
                token=self.token,
                application_id=str(self.application_id),
            )
            self.responded = True
            self.message = msg = Message(**res, _client=self._client)

        return msg if msg is not None else Message(**payload, _client=self._client)

    async def send(self, content: Optional[str] = MISSING, **kwargs) -> Message:
        payload, files = await super().send(content, **kwargs)

        if not self.deferred:
            self.callback = InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE

        _payload: dict = {"type": self.callback.value, "data": payload}

        msg = None
        if self.responded:
            res = await self._client._post_followup(
                data=payload,
                files=files,
                token=self.token,
                application_id=str(self.application_id),
            )
            self.message = msg = Message(**res, _client=self._client)
        else:
            await self._client.create_interaction_response(
                token=self.token,
                application_id=int(self.id),
                data=_payload,
                files=files,
            )

            try:
                _msg = await self._client.get_original_interaction_response(
                    self.token, str(self.application_id)
                )
            except LibraryException:
                pass
            else:
                self.message = msg = Message(**_msg, _client=self._client)

            self.responded = True

        return msg if msg is not None else Message(**payload, _client=self._client)

    async def defer(
        self, ephemeral: Optional[bool] = False, edit_origin: Optional[bool] = False
    ) -> Message:
        """
        .. versionchanged:: 4.4.0
            Now returns the created message object

        This "defers" a component response, allowing up
        to a 15-minute delay between invocation and responding.

        :param Optional[bool] ephemeral: Whether the deferred state is hidden or not.
        :param Optional[bool] edit_origin: Whether you want to edit the original message or send a followup message
        :return: The deferred message
        :rtype: Message
        """
        if not self.responded:

            self.deferred = True
            _ephemeral: int = MessageFlags.EPHEMERAL.value if bool(ephemeral) else 0
            # ephemeral doesn't change callback typings. just data json
            if edit_origin:
                self.callback = InteractionCallbackType.DEFERRED_UPDATE_MESSAGE
            else:
                self.callback = InteractionCallbackType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE

            await self._client.create_interaction_response(
                token=self.token,
                application_id=int(self.id),
                data={"type": self.callback.value, "data": {"flags": _ephemeral}},
            )
            try:
                _msg = await self._client.get_original_interaction_response(
                    self.token, str(self.application_id)
                )
            except LibraryException:
                pass
            else:
                self.message = Message(**_msg, _client=self._client)
            self.responded = True
            return self.message

    async def disable_all_components(
        self, respond_to_interaction: Optional[bool] = True, **other_kwargs: Optional[dict]
    ) -> Message:
        r"""
        .. versionadded:: 4.3.2

        Disables all components of the message.

        :param Optional[bool] respond_to_interaction: Whether the components should be disabled in an interaction response, default True
        :param Optional[dict] \**other_kwargs: Additional keyword-arguments to pass to the edit method. This only works when this method is used as interaction response and takes the same arguments as :func:`ComponentContext.edit()`

        :return: The modified Message
        :rtype: Message
        """

        if not respond_to_interaction:
            return await self.message.disable_all_components()

        for components in self.message.components:
            for component in components.components:
                component.disabled = True

        if other_kwargs.get("components"):
            raise LibraryException(
                12, "You must not specify the `components` argument in this method."
            )

        other_kwargs["components"] = self.message.components
        return await self.edit(**other_kwargs)

    @property
    def custom_id(self) -> Optional[str]:
        """
        The custom ID of the interacted component.

        :rtype: Optional[str]
        """
        return self.data.custom_id

    @property
    def label(self) -> Optional[str]:
        """
        The label of the interacted button.

        :rtype: Optional[str]
        """
        if self.data.component_type != ComponentType.BUTTON:
            return
        if self.message is None:
            return
        if self.message.components is None:
            return
        for action_row in self.message.components:
            for component in action_row.components:
                if component.custom_id == self.custom_id:
                    return component.label
