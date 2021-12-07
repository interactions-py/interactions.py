from logging import Logger, StreamHandler, basicConfig, getLogger
from typing import List, Optional, Union

import interactions.client

from .api.http import HTTPClient, Route
from .api.models.channel import Channel
from .api.models.guild import Guild
from .api.models.member import Member
from .api.models.message import Embed, Message, MessageInteraction, MessageReference
from .api.models.misc import DictSerializerMixin, Snowflake
from .api.models.user import User
from .base import CustomFormatter, Data
from .enums import ComponentType, InteractionCallbackType, InteractionType
from .models.command import Choice
from .models.component import ActionRow, Button, Component, Modal, SelectMenu
from .models.misc import InteractionData

basicConfig(level=Data.LOGGER)
log: Logger = getLogger("context")
stream: StreamHandler = StreamHandler()
stream.setLevel(Data.LOGGER)
stream.setFormatter(CustomFormatter())
log.addHandler(stream)


class Context(DictSerializerMixin):
    r"""
    The base class of "context" for dispatched event data
    from the gateway. The premise of having this class is so
    that the user-facing API is able to allow developers to
    easily access information presented from any event in
    a "contextualized" sense.

    :ivar Optional[Message] message?: The message data model.
    :ivar Member author: The member data model.
    :ivar User user: The user data model.
    :ivar Channel channel: The channel data model.
    :ivar Guild guild: The guild data model.
    """

    __slots__ = ("message", "member", "author", "user", "channel", "guild", "client")

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.message = Message(**self.message) if self._json.get("message") else None
        self.member = Member(**self.member) if self._json.get("member") else None
        self.author = self.member
        self.user = User(**self.user) if self._json.get("user") else None
        self.channel = Channel(**self.channel) if self._json.get("channel") else None
        self.guild = Guild(**self.guild) if self._json.get("guild") else None
        self.client = HTTPClient(interactions.client._token)


class CommandContext(Context):
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
    :ivar str name: The name of the command in the interaction.
    :ivar Optional[str] description?: The description of the command in the interaction.
    :ivar Optional[List[Option]] options?: The options of the command in the interaction, if any.
    :ivar InteractionData data: The application command data.
    :ivar str token: The token of the interaction response.
    :ivar bool responded: Whether an original response was made or not.
    :ivar bool deferred: Whether the response was deferred or not.
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
        "custom_id",
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
    )

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.application_id = (
            Snowflake(self.application_id) if self._json.get("application_id") else None
        )
        self.guild_id = Snowflake(self.guild_id) if self._json.get("guild_id") else None
        self.channel_id = Snowflake(self.channel_id) if self._json.get("channel_id") else None
        self.callback = None
        self.type = InteractionType(self.type)
        self.data = InteractionData(**self.data) if self._json.get("data") else None

        if self._json.get("data").get("target_id"):
            self.target = str(self.data.target_id)

            if str(self.data.target_id) in self.data.resolved.users:
                self.target = self.data.resolved.users[self.target]
            elif str(self.data.target_id) in self.data.resolved.members:
                self.target = self.data.resolved.members[self.target]
            else:
                self.target = self.data.resolved.messages[self.target]

        self.responded = False
        self.deferred = False

    async def defer(self, ephemeral: Optional[bool] = False) -> None:
        """
        This "defers" an interaction response, allowing up
        to a 15-minute delay between invocation and responding.

        :param ephemeral?: Whether the deferred state is hidden or not.
        :type ephemeral: Optional[bool]
        """
        self.deferred = True
        _ephemeral: int = (1 << 6) if bool(ephemeral) else 0
        if bool(ephemeral):
            if self.type == InteractionType.MESSAGE_COMPONENT:
                self.callback = InteractionCallbackType.DEFERRED_UPDATE_MESSAGE
            elif self.type == InteractionType.APPLICATION_COMMAND:
                self.callback = InteractionCallbackType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE
        else:
            if self.type == InteractionType.MESSAGE_COMPONENT:
                self.callback = InteractionCallbackType.UPDATE_MESSAGE
            elif self.type == InteractionType.APPLICATION_COMMAND:
                self.callback = InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE

        await self.client.create_interaction_response(
            token=self.token,
            application_id=int(self.id),
            data={"type": self.callback.value, "data": {"flags": _ephemeral}},
        )

    async def send(
        self,
        content: Optional[str] = None,
        *,
        tts: Optional[bool] = False,
        # attachments: Optional[List[Any]] = None,  # TODO: Replace with own file type.
        embeds: Optional[Union[Embed, List[Embed]]] = None,
        allowed_mentions: Optional[MessageInteraction] = None,
        components: Optional[Union[Component, List[Component]]] = None,
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
        :type components: Optional[Union[Component, List[Component]]]
        :param ephemeral?: Whether the response is hidden or not.
        :type ephemeral: Optional[bool]
        :return: The sent message as an object.
        :rtype: Message
        """
        _content: str = "" if content is None else content
        _tts: bool = False if tts is None else tts
        # _file = None if file is None else file
        # _attachments = [] if attachments else None
        _embeds: list = (
            []
            if embeds is None
            else ([embed._json for embed in embeds] if isinstance(embeds, list) else [embeds._json])
        )
        _allowed_mentions: dict = {} if allowed_mentions is None else allowed_mentions
        _components: list = [{"type": 1, "components": []}]

        if isinstance(components, ActionRow):
            _components[0]["components"] = [component._json for component in components.components]
        elif isinstance(components, (Button, SelectMenu)):
            _components[0]["components"] = [] if components is None else [components._json]
        else:
            _components = [] if components is None else [components]

        _ephemeral: int = (1 << 6) if bool(ephemeral) else 0

        if not self.deferred:
            self.callback = (
                InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE
                if self.type == InteractionType.APPLICATION_COMMAND
                else InteractionCallbackType.UPDATE_MESSAGE
            )

        # TODO: Add attachments into Message obj.
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
        _payload: dict = {"type": self.callback.value, "data": payload._json}

        async def func():
            if self.responded or self.deferred:
                await self.client._req.request(
                    Route(
                        "PATCH", f"/webhooks/{self.application_id}/{self.token}/messages/@original"
                    ),
                    json=_payload,
                )
            else:
                await self.client.create_interaction_response(
                    token=self.token,
                    application_id=str(self.id),
                    data=_payload,
                )
                self.responded = True

        await func()
        return payload

    async def edit(
        self,
        content: Optional[str] = None,
        *,
        tts: Optional[bool] = None,
        # file: Optional[FileIO] = None,
        embeds: Optional[Union[Embed, List[Embed]]] = None,
        allowed_mentions: Optional[MessageInteraction] = None,
        message_reference: Optional[MessageReference] = None,
        components: Optional[Union[ActionRow, Button, SelectMenu]] = None,
    ) -> Message:
        """
        This allows the invocation state described in the "context"
        to send an interaction response. This inherits the arguments
        of the ``.send()`` method.

        :inherit:`interactions.context.CommandContext.send()`
        :return: The edited message as an object.
        :rtype: Message
        """
        _content: str = "" if content is None else content
        _tts: bool = False if tts is None else tts
        # _file = None if file is None else file
        _embeds: list = (
            []
            if embeds is None
            else ([embed._json for embed in embeds] if isinstance(embeds, list) else [embeds._json])
        )
        _allowed_mentions: dict = {} if allowed_mentions is None else allowed_mentions
        _message_reference: dict = {} if message_reference is None else message_reference._json
        _components: list = [{"type": 1, "components": []}]

        if isinstance(components, ActionRow):
            _components[0]["components"] = [component._json for component in components.components]
        elif isinstance(components, (Button, SelectMenu)):
            _components[0]["components"] = [] if components is None else [components._json]
        else:
            _components = []

        _type = (
            InteractionCallbackType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE.value
            if self.deferred
            else InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE.value
        )

        payload: Message = Message(
            content=_content,
            tts=_tts,
            # file=file,
            embeds=_embeds,
            allowed_mentions=_allowed_mentions,
            message_reference=_message_reference,
            components=_components,
            flags=self.message.ephemeral,
        )

        async def func():
            if self.type == InteractionType.MESSAGE_COMPONENT:
                await self.client._post_followup(
                    data=payload._json, token=self.token, application_id=self.application_id
                )
            else:
                await self.client.edit_interaction_response(
                    token=self.token,
                    application_id=str(self.id),
                    data={"type": _type, "data": payload._json},
                    message_id=self.message.id,
                )
            self.message = payload

        await func()
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
                webhook_id=str(self.id), webhook_token=self.token, message_id=self.message.id
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
                # elif all(isinstance(choice, Dict[str, Any]) for choice in choices):
                elif all(
                    isinstance(choice, dict) and all(isinstance(x, str) for x in choice)
                    for choice in choices
                ):
                    _choices = [choice for choice in choices]
                elif isinstance(choices, Choice):
                    _choices = [choices._json]
                else:
                    _choices = [choices]

                await self.client.create_interaction_response(
                    token=self.token,
                    application_id=str(self.id),
                    data={
                        "type": InteractionCallbackType.APPLICATION_COMMAND_AUTOCOMPLETE_RESULT.value,
                        "data": {"choices": _choices},
                    },
                )

                return _choices

        return await func()

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
            application_id=str(self.id),
            data=payload,
        )


class ComponentContext(CommandContext):
    """
    A derivation of :class:`interactions.context.CommandContext`
    designed specifically for component data.
    """

    __slots__ = (
        "message",
        "author",
        "user",
        "channel",
        "guild",
        "client",
        "id",
        "application_id",
        "type",
        "name",
        "description",
        "options",
        "data",
        "responded",
        "deferred",
        "custom_id",
    )

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.type = ComponentType(self.type)
        self.responded = False  # remind components that it was not responded to.
