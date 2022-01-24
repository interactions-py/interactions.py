from logging import Logger
from typing import List, Optional, Union

from .api.models.channel import Channel
from .api.models.guild import Guild
from .api.models.member import Member
from .api.models.message import Embed, Message, MessageInteraction, MessageReference
from .api.models.misc import DictSerializerMixin, Snowflake
from .api.models.user import User
from .base import get_logger
from .enums import InteractionCallbackType, InteractionType
from .models.command import Choice
from .models.component import ActionRow, Button, Modal, SelectMenu
from .models.misc import InteractionData

log: Logger = get_logger("context")


class Context(DictSerializerMixin):
    """
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
        self.message = (
            Message(**self.message, _client=self.client) if self._json.get("message") else None
        )
        self.member = (
            Member(**self.member, _client=self.client) if self._json.get("member") else None
        )
        self.author = self.member
        self.user = User(**self.user) if self._json.get("user") else None

        # TODO: The below attributes are always None because they aren't by API return.
        self.channel = Channel(**self.channel) if self._json.get("channel") else None
        self.guild = Guild(**self.guild) if self._json.get("guild") else None


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
    :ivar Snowflake channel_id: The ID of the current channel.
    :ivar Snowflake guild_id: The ID of the current guild.
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
        #
        "locale",
        "guild_locale",
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
        _ephemeral: int = (1 << 6) if ephemeral else 0
        if self.type == InteractionType.MESSAGE_COMPONENT:
            self.callback = InteractionCallbackType.DEFERRED_UPDATE_MESSAGE
        elif self.type == InteractionType.APPLICATION_COMMAND:
            self.callback = InteractionCallbackType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE

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
        # attachments: Optional[List[Any]] = None,  # TODO: post-v4: Replace with own file type.
        embeds: Optional[Union[Embed, List[Embed]]] = None,
        allowed_mentions: Optional[MessageInteraction] = None,
        components: Optional[
            Union[ActionRow, Button, SelectMenu, List[Union[ActionRow, Button, SelectMenu]]]
        ] = None,
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
            content is None
            and self.message
            and self.callback == InteractionCallbackType.DEFERRED_UPDATE_MESSAGE
        ):
            _content = self.message.content
        else:
            _content: str = "" if content is None else content
        _tts: bool = False if tts is None else tts
        # _file = None if file is None else file
        # _attachments = [] if attachments else None
        if embeds is None and self.message:
            _embeds = self.message.embeds
        else:
            _embeds: list = (
                []
                if embeds is None
                else (
                    [embed._json for embed in embeds]
                    if isinstance(embeds, list)
                    else [embeds._json]
                )
            )
        _allowed_mentions: dict = {} if allowed_mentions is None else allowed_mentions
        _components: List[dict] = [{"type": 1, "components": []}]

        # TODO: Break this obfuscation pattern down to a "builder" method.
        if components:
            if isinstance(components, list) and all(
                isinstance(action_row, ActionRow) for action_row in components
            ):
                _components = [
                    {
                        "type": 1,
                        "components": [
                            (
                                component._json
                                if component._json.get("custom_id") or component._json.get("url")
                                else []
                            )
                            for component in action_row.components
                        ],
                    }
                    for action_row in components
                ]
            elif isinstance(components, list) and all(
                isinstance(component, (Button, SelectMenu)) for component in components
            ):
                for component in components:
                    if isinstance(component, SelectMenu):
                        component._json["options"] = [
                            options._json if not isinstance(options, dict) else options
                            for options in component._json["options"]
                        ]
                _components = [
                    {
                        "type": 1,
                        "components": [
                            (
                                component._json
                                if component._json.get("custom_id") or component._json.get("url")
                                else []
                            )
                            for component in components
                        ],
                    }
                ]
            elif isinstance(components, list) and all(
                isinstance(action_row, (list, ActionRow)) for action_row in components
            ):
                _components = []
                for action_row in components:
                    for component in (
                        action_row if isinstance(action_row, list) else action_row.components
                    ):
                        if isinstance(component, SelectMenu):
                            component._json["options"] = [
                                option._json for option in component.options
                            ]
                    _components.append(
                        {
                            "type": 1,
                            "components": [
                                (
                                    component._json
                                    if component._json.get("custom_id")
                                    or component._json.get("url")
                                    else []
                                )
                                for component in (
                                    action_row
                                    if isinstance(action_row, list)
                                    else action_row.components
                                )
                            ],
                        }
                    )
            elif isinstance(components, ActionRow):
                _components[0]["components"] = [
                    (
                        component._json
                        if component._json.get("custom_id") or component._json.get("url")
                        else []
                    )
                    for component in components.components
                ]
            elif isinstance(components, Button):
                _components[0]["components"] = (
                    [components._json]
                    if components._json.get("custom_id") or components._json.get("url")
                    else []
                )
            elif isinstance(components, SelectMenu):
                components._json["options"] = [
                    options._json if not isinstance(options, dict) else options
                    for options in components._json["options"]
                ]
                _components[0]["components"] = (
                    [components._json]
                    if components._json.get("custom_id") or components._json.get("url")
                    else []
                )
        elif components is None and self.message:
            _components = self.message.components
        else:
            _components = []

        _ephemeral: int = (1 << 6) if ephemeral else 0

        if not self.deferred and self.type != InteractionType.MESSAGE_COMPONENT:
            self.callback = (
                InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE
                if self.type == InteractionType.APPLICATION_COMMAND
                else InteractionCallbackType.UPDATE_MESSAGE
            )

        if not self.deferred and self.type == InteractionType.MESSAGE_COMPONENT:
            self.callback = InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE

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
        _payload: dict = {"type": self.callback.value, "data": payload._json}

        async def func():
            if (
                self.responded
                or self.deferred
                or self.type == InteractionType.MESSAGE_COMPONENT
                and self.callback == InteractionCallbackType.DEFERRED_UPDATE_MESSAGE
            ):
                if (
                    self.type == InteractionType.APPLICATION_COMMAND
                    and self.deferred
                    or self.type == InteractionType.MESSAGE_COMPONENT
                    and self.deferred
                ):
                    res = await self.client.edit_interaction_response(
                        data=payload._json,
                        token=self.token,
                        application_id=str(self.application_id),
                    )
                    self.responded = True
                    self.message = Message(**res, _client=self.client)
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
        components: Optional[
            Union[ActionRow, Button, SelectMenu, List[Union[ActionRow, Button, SelectMenu]]]
        ] = None,
    ) -> Message:
        """
        This allows the invocation state described in the "context"
        to send an interaction response. This inherits the arguments
        of the ``.send()`` method.

        :inherit:`interactions.context.CommandContext.send()`
        :return: The edited message as an object.
        :rtype: Message
        """
        _content: str = self.message.content if content is None else content
        _tts: bool = False if tts is None else tts
        # _file = None if file is None else file

        if embeds is None:
            _embeds = self.message.embeds
        else:
            _embeds: list = (
                []
                if embeds is None
                else (
                    [embed._json for embed in embeds]
                    if isinstance(embeds, list)
                    else [embeds._json]
                )
            )
        _allowed_mentions: dict = {} if allowed_mentions is None else allowed_mentions
        _message_reference: dict = {} if message_reference is None else message_reference._json

        if components is None:
            _components = self.message.components
        elif components == []:
            _components = []
        else:
            _components: list = [{"type": 1, "components": []}]
            if (
                isinstance(components, list)
                and components
                and all(isinstance(action_row, ActionRow) for action_row in components)
            ):
                _components = [
                    {
                        "type": 1,
                        "components": [
                            (
                                component._json
                                if component._json.get("custom_id") or component._json.get("url")
                                else []
                            )
                            for component in action_row.components
                        ],
                    }
                    for action_row in components
                ]
            elif (
                isinstance(components, list)
                and components
                and all(isinstance(component, (Button, SelectMenu)) for component in components)
            ):
                if isinstance(components[0], SelectMenu):
                    components[0]._json["options"] = [
                        option._json for option in components[0].options
                    ]
                _components = [
                    {
                        "type": 1,
                        "components": [
                            (
                                component._json
                                if component._json.get("custom_id") or component._json.get("url")
                                else []
                            )
                            for component in components
                        ],
                    }
                ]
            elif (
                isinstance(components, list)
                and components
                and all(isinstance(action_row, (list, ActionRow)) for action_row in components)
            ):
                _components = []
                for action_row in components:
                    for component in (
                        action_row if isinstance(action_row, list) else action_row.components
                    ):
                        if isinstance(component, SelectMenu):
                            component._json["options"] = [
                                option._json for option in component.options
                            ]
                    _components.append(
                        {
                            "type": 1,
                            "components": [
                                (
                                    component._json
                                    if component._json.get("custom_id")
                                    or component._json.get("url")
                                    else []
                                )
                                for component in (
                                    action_row
                                    if isinstance(action_row, list)
                                    else action_row.components
                                )
                            ],
                        }
                    )
            elif isinstance(components, ActionRow):
                _components[0]["components"] = [
                    (
                        component._json
                        if component._json.get("custom_id") or component._json.get("url")
                        else []
                    )
                    for component in components.components
                ]
            elif isinstance(components, (Button, SelectMenu)):
                _components[0]["components"] = (
                    [components._json]
                    if components._json.get("custom_id") or components._json.get("url")
                    else []
                )
            else:
                _components = []

        payload: Message = Message(
            content=_content,
            tts=_tts,
            # file=file,
            embeds=_embeds,
            allowed_mentions=_allowed_mentions,
            message_reference=_message_reference,
            components=_components,
        )

        async def func():
            if not self.deferred and self.type == InteractionType.MESSAGE_COMPONENT:
                self.callback = InteractionCallbackType.UPDATE_MESSAGE
                await self.client.create_interaction_response(
                    data={"type": self.callback.value, "data": payload._json},
                    token=self.token,
                    application_id=int(self.id),
                )
                self.message = payload
                self.responded = True
            elif self.deferred:
                if (
                    self.type == InteractionType.MESSAGE_COMPONENT
                    and self.callback != InteractionCallbackType.DEFERRED_UPDATE_MESSAGE
                ):
                    await self.client._post_followup(
                        data=payload._json,
                        token=self.token,
                        application_id=str(self.application_id),
                    )
                elif (
                    self.callback == InteractionCallbackType.DEFERRED_UPDATE_MESSAGE
                    and self.type == InteractionType.MESSAGE_COMPONENT
                ):
                    res = await self.client.edit_interaction_response(
                        data=payload._json,
                        token=self.token,
                        application_id=str(self.application_id),
                    )
                    self.responded = True
                    self.message = Message(**res, _client=self.client)
                elif hasattr(self.message, "id") and self.message.id is not None:
                    res = await self.client.edit_message(
                        int(self.channel_id), int(self.message.id), payload=payload._json
                    )
                    self.message = Message(**res, _client=self.client)
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
                        self.message = Message(**res, _client=self.client)
            else:
                self.callback = (
                    InteractionCallbackType.UPDATE_MESSAGE
                    if self.type == InteractionType.MESSAGE_COMPONENT
                    else self.callback
                )
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
                    self.message = Message(**res, _client=self.client)

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
                    _choices = [choices]

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


class ComponentContext(CommandContext):
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
        #
        "locale",
        "guild_locale",
    )

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.responded = False  # remind components that it was not responded to.
        self.deferred = False  # remind components they not have been deferred

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
        if self.type == InteractionType.MESSAGE_COMPONENT:
            if edit_origin:
                self.callback = InteractionCallbackType.DEFERRED_UPDATE_MESSAGE
            else:
                self.callback = InteractionCallbackType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE

        await self.client.create_interaction_response(
            token=self.token,
            application_id=int(self.id),
            data={"type": self.callback.value, "data": {"flags": _ephemeral}},
        )
