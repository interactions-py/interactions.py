from logging import Logger
from typing import List, Optional, Union

from .api import InteractionException
from .api.models.channel import Channel
from .api.models.guild import Guild
from .api.models.member import Member
from .api.models.message import Embed, Message, MessageInteraction, MessageReference
from .api.models.misc import MISSING, DictSerializerMixin, Snowflake
from .api.models.user import User
from .base import get_logger
from .enums import InteractionCallbackType, InteractionType
from .models.command import Choice
from .models.component import ActionRow, Button, Modal, SelectMenu, _build_components
from .models.misc import InteractionData

log: Logger = get_logger("context")


class _Context(DictSerializerMixin):
    """
    The base class of "context" for dispatched event data
    from the gateway. The premise of having this class is so
    that the user-facing API is able to allow developers to
    easily access information presented from any event in
    a "contextualized" sense.

    :ivar Optional[Message] message?: The message data model.
    :ivar Member author: The member data model.
    :ivar User user: The user data model.
    :ivar Optional[Channel] channel: The channel data model.
    :ivar Optional[Guild] guild: The guild data model.
    """

    __slots__ = (
        "message",
        "member",
        "author",
        "user",
        "channel",
        "channel_id",
        "guild",
        "guild_id",
        "client",
        "id",
        "application_id",
        "type",
        "data",
        "token",
    )

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.message = (
            Message(**self.message, _client=self.client) if self._json.get("message") else None
        )
        self.member = (
            Member(**self.member, _client=self.client) if self._json.get("member") else None
        )
        self.author = self.member
        self.user = User(**self.user) if self._json.get("user") else None

        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.application_id = (
            Snowflake(self.application_id) if self._json.get("application_id") else None
        )
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.channel_id = Snowflake(self.channel_id) if self._json.get("channel_id") else None
        self.callback = None
        self.type = InteractionType(self.type)
        self.data = InteractionData(**self.data) if self._json.get("data") else None

        if guild := self._json.get("guild"):
            self.guild = Guild(**guild)
        elif self.guild_id is None:
            self.guild = None
        elif guild := self.client.cache.guilds.get(self.guild_id):
            self.guild = guild
        else:
            self.guild = MISSING

        if channel := self._json.get("channel"):
            self.channel = Channel(**channel)
        elif channel := self.client.cache.channels.get(self.channel_id):
            self.channel = channel
        else:
            self.channel = MISSING

        self.responded = False
        self.deferred = False

    async def get_channel(self) -> Channel:
        """
        This gets the channel the context was invoked in.

        :return: The channel as object
        :rtype: Channel
        """

        res = await self.client.get_channel(int(self.channel_id))
        self.channel = Channel(**res, _client=self.client)
        return self.channel

    async def get_guild(self) -> Guild:
        """
        This gets the guild the context was invoked in.

        :return: The guild as object
        :rtype: Guild
        """

        res = await self.client.get_guild(int(self.guild_id))
        self.guild = Guild(**res, _client=self.client)
        return self.guild

    async def send(
        self,
        content: Optional[str] = MISSING,
        *,
        tts: Optional[bool] = MISSING,
        # attachments: Optional[List[Any]] = None,  # TODO: post-v4: Replace with own file type.
        embeds: Optional[Union[Embed, List[Embed]]] = MISSING,
        allowed_mentions: Optional[MessageInteraction] = MISSING,
        components: Optional[
            Union[ActionRow, Button, SelectMenu, List[ActionRow], List[Button], List[SelectMenu]]
        ] = MISSING,
        ephemeral: Optional[bool] = False,
    ) -> Message:
        """
        This allows the invocation state described in the "context"
        to send an interaction response.

        :param content?: The contents of the message as a string or string-converted value.
        :type content: Optional[str]
        :param tts?: Whether the message utilizes the text-to-speech Discord programme or not.
        :type tts: Optional[bool]
        :param embeds?: An embed, or list of embeds for the message.
        :type embeds: Optional[Union[Embed, List[Embed]]]
        :param allowed_mentions?: The message interactions/mention limits that the message can refer to.
        :type allowed_mentions: Optional[MessageInteraction]
        :param components?: A component, or list of components for the message.
        :type components: Optional[Union[ActionRow, Button, SelectMenu, List[Union[ActionRow, Button, SelectMenu]]]]
        :param ephemeral?: Whether the response is hidden or not.
        :type ephemeral: Optional[bool]
        :return: The sent message as an object.
        :rtype: Message
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
        # _file = None if file is None else file
        # _attachments = [] if attachments else None

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
        _allowed_mentions: dict = {} if allowed_mentions is MISSING else allowed_mentions

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

        _ephemeral: int = (1 << 6) if ephemeral else 0

        # TODO: post-v4: Add attachments into Message obj.
        payload: Message = Message(
            content=_content,
            tts=_tts,
            # file=file,
            # attachments=_attachments,
            embeds=_embeds,
            allowed_mentions=_allowed_mentions,
            components=_components,
            flags=_ephemeral,
        )
        self.message = payload
        self.message._client = self.client
        return payload

    async def edit(
        self,
        content: Optional[str] = MISSING,
        *,
        tts: Optional[bool] = MISSING,
        # file: Optional[FileIO] = None,
        embeds: Optional[Union[Embed, List[Embed]]] = MISSING,
        allowed_mentions: Optional[MessageInteraction] = MISSING,
        message_reference: Optional[MessageReference] = MISSING,
        components: Optional[
            Union[ActionRow, Button, SelectMenu, List[ActionRow], List[Button], List[SelectMenu]]
        ] = MISSING,
    ) -> Message:
        """
        This allows the invocation state described in the "context"
        to send an interaction response. This inherits the arguments
        of the ``.send()`` method.

        :inherit:`interactions.context.CommandContext.send()`
        :return: The edited message as an object.
        :rtype: Message
        """

        payload = {}

        if self.message.content is not None or content is not MISSING:
            _content: str = self.message.content if content is MISSING else content
            payload["content"] = _content
        _tts: bool = False if tts is MISSING else tts
        payload["tts"] = _tts
        # _file = None if file is None else file

        if self.message.embeds is not None or embeds is not MISSING:
            if embeds is MISSING:
                embeds = self.message.embeds
            _embeds: list = (
                []
                if not embeds
                else (
                    [embed._json for embed in embeds]
                    if isinstance(embeds, list)
                    else [embeds._json]
                )
            )
            payload["embeds"] = _embeds

        _allowed_mentions: dict = {} if allowed_mentions is MISSING else allowed_mentions
        _message_reference: dict = {} if message_reference is MISSING else message_reference._json

        payload["allowed_mentions"] = _allowed_mentions
        payload["message_reference"] = _message_reference

        if self.message.components is not None or components is not MISSING:
            if components is MISSING:
                _components = self.message.components
            elif not components:
                _components = []
            else:
                _components = _build_components(components=components)

            payload["components"] = _components

        payload = Message(**payload)
        self.message._client = self.client

        return payload

    async def popup(self, modal: Modal) -> None:
        """
        This "pops up" a modal to present information back to the
        user.

        :param modal: The components you wish to show.
        :type modal: Modal
        """

        payload: dict = {
            "type": InteractionCallbackType.MODAL.value,
            "data": {
                "title": modal.title,
                "components": modal._json.get("components"),
                "custom_id": modal.custom_id,
            },
        }

        await self.client.create_interaction_response(
            token=self.token,
            application_id=int(self.id),
            data=payload,
        )
        self.responded = True

        return payload


class CommandContext(_Context):
    """
    A derivation of :class:`interactions.context.Context`
    designed specifically for application command data.

    .. warning::
        The ``guild`` attribute of the base context
        is not accessible for any interaction-related events
        since the current Discord API schema does not return
        this as a value, but instead ``guild_id``. You will
        need to manually fetch for this data for the time being.

        You can fetch with ``client.get_guild(guild_id)`` which
        will return a JSON dictionary, which you can then use
        ``interactions.Guild(**data)`` for an object or continue
        with a dictionary for your own purposes.

    :ivar Snowflake id: The ID of the interaction.
    :ivar Snowflake application_id: The application ID of the interaction.
    :ivar InteractionType type: The type of interaction.
    :ivar InteractionData data?: The application command data.
    :ivar Optional[Union[Message, Member, User]] target: The target selected if this interaction is invoked as a context menu.
    :ivar str token: The token of the interaction response.
    :ivar Snowflake guild_id?: The ID of the current guild.
    :ivar Snowflake channel_id?: The ID of the current channel.
    :ivar bool responded: Whether an original response was made or not.
    :ivar bool deferred: Whether the response was deferred or not.
    :ivar str locale?: The selected language of the user invoking the interaction.
    :ivar str guild_locale?: The guild's preferred language, if invoked in a guild.
    """

    __slots__ = (
        "message",
        "member",
        "author",
        "user",
        "channel",
        "guild",
        "client",
        "id",
        "application_id",
        "callback",
        "type",
        "data",
        "target",
        "version",
        "token",
        "guild_id",
        "channel_id",
        "responded",
        "deferred",
        "locale",
        "guild_locale",
    )

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        if self._json.get("data").get("target_id"):
            self.target = str(self.data.target_id)

            if self.data.type == 2:
                if (
                    self._json.get("guild_id")
                    and str(self.data.target_id) in self.data.resolved.members
                ):
                    # member id would have potential to exist, and therefore have target def priority.
                    self.target = self.data.resolved.members[self.target]
                else:
                    self.target = self.data.resolved.users[self.target]
            elif self.data.type == 3:
                self.target = self.data.resolved.messages[self.target]

    async def edit(self, content: Optional[str] = MISSING, **kwargs) -> Message:

        payload = await super().edit(content, **kwargs)
        msg = None

        if self.deferred:
            if hasattr(self.message, "id") and self.message.id is not None:
                res = await self.client.edit_message(
                    int(self.channel_id), int(self.message.id), payload=payload._json
                )
                self.message = msg = Message(**res, _client=self.client)
            else:
                res = await self.client.edit_interaction_response(
                    token=self.token,
                    application_id=str(self.id),
                    data={"type": self.callback.value, "data": payload._json},
                    message_id=self.message.id if self.message else "@original",
                )
                if res["flags"] == 64:
                    log.warning("You can't edit hidden messages.")
                    self.message = payload
                    self.message._client = self.client
                else:
                    await self.client.edit_message(
                        int(self.channel_id), res["id"], payload=payload._json
                    )
                    self.message = msg = Message(**res, _client=self.client)
        else:
            res = await self.client.edit_interaction_response(
                token=self.token,
                application_id=str(self.application_id),
                data={"type": self.callback.value, "data": payload._json},
            )
            if res["flags"] == 64:
                log.warning("You can't edit hidden messages.")
            else:
                await self.client.edit_message(
                    int(self.channel_id), res["id"], payload=payload._json
                )
                self.message = msg = Message(**res, _client=self.client)

        if msg is not None:
            return msg
        return payload

    async def defer(self, ephemeral: Optional[bool] = False) -> None:
        """
        This "defers" an interaction response, allowing up
        to a 15-minute delay between invocation and responding.

        :param ephemeral?: Whether the deferred state is hidden or not.
        :type ephemeral: Optional[bool]
        """
        self.deferred = True
        _ephemeral: int = (1 << 6) if ephemeral else 0
        self.callback = InteractionCallbackType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE

        await self.client.create_interaction_response(
            token=self.token,
            application_id=int(self.id),
            data={"type": self.callback.value, "data": {"flags": _ephemeral}},
        )

    async def send(self, content: Optional[str] = MISSING, **kwargs) -> Message:
        payload = await super().send(content, **kwargs)

        if not self.deferred:
            self.callback = InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE

        _payload: dict = {"type": self.callback.value, "data": payload._json}

        msg = None
        if self.responded or self.deferred:
            if self.deferred:
                res = await self.client.edit_interaction_response(
                    data=payload._json,
                    token=self.token,
                    application_id=str(self.application_id),
                )
                self.responded = True
                self.message = msg = Message(**res, _client=self.client)
            else:
                await self.client._post_followup(
                    data=payload._json,
                    token=self.token,
                    application_id=str(self.application_id),
                )
        else:
            await self.client.create_interaction_response(
                token=self.token,
                application_id=int(self.id),
                data=_payload,
            )
            __newdata = await self.client.edit_interaction_response(
                data={},
                token=self.token,
                application_id=str(self.application_id),
            )
            if not __newdata.get("code"):
                # if sending message fails somehow
                msg = Message(**__newdata, _client=self.client)
                self.message = msg
            self.responded = True
        if msg is not None:
            return msg
        return payload

    async def delete(self) -> None:
        """
        This deletes the interaction response of a message sent by
        the contextually derived information from this class.

        .. note::
            Doing this will proceed in the context message no longer
            being present.
        """
        if self.responded:
            await self.client.delete_webhook_message(
                webhook_id=int(self.id), webhook_token=self.token, message_id=int(self.message.id)
            )
        else:
            await self.client.delete_original_webhook_message(int(self.id), self.token)
        self.message = None

    async def populate(self, choices: Union[Choice, List[Choice]]) -> List[Choice]:
        """
        This "populates" the list of choices that the client-end
        user will be able to select from in the autocomplete field.

        .. warning::
            Only a maximum of ``25`` choices may be presented
            within an autocomplete option.

        :param choices: The choices you wish to present.
        :type choices: Union[Choice, List[Choice]]
        :return: The list of choices you've given.
        :rtype: List[Choice]
        """

        async def func():
            if choices:
                _choices: list = []
                if all(isinstance(choice, Choice) for choice in choices):
                    _choices = [choice._json for choice in choices]
                elif all(
                    isinstance(choice, dict) and all(isinstance(x, str) for x in choice)
                    for choice in choices
                ):
                    _choices = list(choices)
                elif isinstance(choices, Choice):
                    _choices = [choices._json]
                else:
                    raise InteractionException(
                        6, message="Autocomplete choice items must be of type Choice"
                    )

                await self.client.create_interaction_response(
                    token=self.token,
                    application_id=int(self.id),
                    data={
                        "type": InteractionCallbackType.APPLICATION_COMMAND_AUTOCOMPLETE_RESULT.value,
                        "data": {"choices": _choices},
                    },
                )

                return _choices

        return await func()


class ComponentContext(_Context):
    """
    A derivation of :class:`interactions.context.CommandContext`
    designed specifically for component data.
    """

    __slots__ = (
        "message",
        "member",
        "author",
        "user",
        "channel",
        "guild",
        "client",
        "id",
        "application_id",
        "callback",
        "type",
        "data",
        "target",
        "version",
        "token",
        "guild_id",
        "channel_id",
        "responded",
        "deferred",
        "locale",
        "guild_locale",
    )

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.responded = False  # remind components that it was not responded to.
        self.deferred = False  # remind components they not have been deferred

    async def edit(self, content: Optional[str] = MISSING, **kwargs) -> Message:

        payload = await super().edit(content, **kwargs)
        msg = None

        if not self.deferred:
            self.callback = InteractionCallbackType.UPDATE_MESSAGE
            await self.client.create_interaction_response(
                data={"type": self.callback.value, "data": payload._json},
                token=self.token,
                application_id=int(self.id),
            )
            self.message = payload
            self.responded = True
        elif self.callback != InteractionCallbackType.DEFERRED_UPDATE_MESSAGE:
            await self.client._post_followup(
                data=payload._json,
                token=self.token,
                application_id=str(self.application_id),
            )
        else:
            res = await self.client.edit_interaction_response(
                data=payload._json,
                token=self.token,
                application_id=str(self.application_id),
            )
            self.responded = True
            self.message = msg = Message(**res, _client=self.client)

        if msg is not None:
            return msg

        return payload

    async def send(self, content: Optional[str] = MISSING, **kwargs) -> Message:
        payload = await super().send(content, **kwargs)

        if not self.deferred:
            self.callback = InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE

        _payload: dict = {"type": self.callback.value, "data": payload._json}

        msg = None
        if (
            self.responded
            or self.deferred
            or self.callback == InteractionCallbackType.DEFERRED_UPDATE_MESSAGE
        ):
            if self.deferred:
                res = await self.client.edit_interaction_response(
                    data=payload._json,
                    token=self.token,
                    application_id=str(self.application_id),
                )
                self.responded = True
                self.message = msg = Message(**res, _client=self.client)
            else:
                await self.client._post_followup(
                    data=payload._json,
                    token=self.token,
                    application_id=str(self.application_id),
                )
        else:
            await self.client.create_interaction_response(
                token=self.token,
                application_id=int(self.id),
                data=_payload,
            )
            __newdata = await self.client.edit_interaction_response(
                data={},
                token=self.token,
                application_id=str(self.application_id),
            )
            if not __newdata.get("code"):
                # if sending message fails somehow
                msg = Message(**__newdata, _client=self.client)
                self.message = msg
            self.responded = True

        if msg is not None:
            return msg
        return payload

    async def defer(
        self, ephemeral: Optional[bool] = False, edit_origin: Optional[bool] = False
    ) -> None:
        """
        This "defers" a component response, allowing up
        to a 15-minute delay between invocation and responding.

        :param ephemeral?: Whether the deferred state is hidden or not.
        :type ephemeral: Optional[bool]
        :param edit_origin?: Whether you want to edit the original message or send a followup message
        :type edit_origin: Optional[bool]
        """
        self.deferred = True
        _ephemeral: int = (1 << 6) if bool(ephemeral) else 0

        # ephemeral doesn't change callback typings. just data json
        if edit_origin:
            self.callback = InteractionCallbackType.DEFERRED_UPDATE_MESSAGE
        else:
            self.callback = InteractionCallbackType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE

        await self.client.create_interaction_response(
            token=self.token,
            application_id=int(self.id),
            data={"type": self.callback.value, "data": {"flags": _ephemeral}},
        )

    @property
    def custom_id(self) -> Optional[str]:
        return self.data.custom_id

    @property
    def label(self) -> Optional[str]:
        for action_row in self.message.components:
            for component in action_row["components"]:
                if component["custom_id"] == self.custom_id and component["type"] == 2:
                    return component.get("label")
