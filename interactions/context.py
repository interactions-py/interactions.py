# from io import FileIO
from typing import Any, Dict, List, Optional, Union

import interactions.client

from .api.http import HTTPClient, Route
from .api.models.channel import Channel
from .api.models.member import Member
from .api.models.message import Embed, Message, MessageInteraction, MessageReference
from .api.models.misc import DictSerializerMixin
from .api.models.user import User
from .enums import InteractionCallbackType, InteractionType
from .models.component import ActionRow, Button, SelectMenu
from .models.misc import InteractionData


class Context(DictSerializerMixin):
    r"""
    The base class of \"context\" for dispatched event data
    from the gateway.

    :ivar Message message: The message data model.
    :ivar Member author: The member data model.
    :ivar User user: The user data model.
    :ivar Channel channel: The channel data model.
    :ivar Guild guild: The guild data model.
    :ivar \*args: Multiple arguments of the context.
    :ivar \**kwargs: Keyword-only arguments of the context.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


class InteractionContext(Context):
    """
    This is a derivation of the base Context class designed specifically for
    interaction data.

    :ivar str id: The ID of the interaction.
    :ivar str application_id: The application ID of the interaction.
    :ivar Union[str, int, InteractionType] type: The type of interaction.
    :ivar InteractionData data: The application command data.
    :ivar str guild_id: The guild ID the interaction falls under.
    :ivar str channel_id: The channel ID the interaction was instantiated from.
    :ivar str token: The token of the interaction response.
    :ivar bool responded: Whether an original response was made or not.
    :ivar bool deferred: Whether the response was deferred or not.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.message = Message(**kwargs["message"]) if kwargs.get("message") else None
        self.author = Member(**kwargs["member"]) if kwargs.get("member") else None
        self.user = User(**kwargs["user"]) if kwargs.get("user") else None
        self.channel = Channel(**kwargs["channel"]) if kwargs.get("channel") else None
        self.id = kwargs.get("id")
        self.application_id = kwargs.get("application_id")
        self.type = InteractionType(int(kwargs["type"])) if kwargs.get("type") else None
        self.data = InteractionData(**kwargs["data"])
        self.guild_id = kwargs.get("guild_id")
        self.channel_id = kwargs.get("channel_id")
        self.token = kwargs.get("token")
        self.responded = False
        self.deferred = False

    async def defer(self, ephemeral: Optional[bool] = None) -> None:
        """
        This \"defers\" an interaction response, allowing up
        to a 15-minute delay between invokation and responding.

        :param ephemeral: Whether the deferred state is hidden or not.
        :type ephemeral: Optional[bool]
        """
        _type: InteractionCallbackType

        if bool(ephemeral):
            _type = InteractionCallbackType.DEFERRED_UPDATE_MESSAGE
            self.deferred = True
        else:
            _type = InteractionCallbackType.UPDATE_MESSAGE

        await HTTPClient(interactions.client.cache.token).create_interaction_response(
            token=self.token, application_id=int(self.id), data={"type": _type.value}
        )

    async def send(
        self,
        content: Optional[str] = None,
        *,
        tts: Optional[bool] = None,
        # file: Optional[FileIO] = None,
        embeds: Optional[Union[Embed, List[Embed]]] = None,
        allowed_mentions: Optional[MessageInteraction] = None,
        message_reference: Optional[MessageReference] = None,
        components: Optional[Union[List[Dict[str, Any]], ActionRow, Button, SelectMenu]] = None,
        sticker_ids: Optional[Union[str, List[str]]] = None,
        type: Optional[Union[int, InteractionCallbackType]] = None,
        ephemeral: Optional[bool] = None,
    ) -> Message:
        """
        This allows the invokation state described in the "context"
        to send an interaction response.

        :param content: The contents of the message as a string or string-converted value.
        :type content: Optional[str]
        :param tts: Whether the message utilizes the text-to-speech Discord programme or not.
        :type tts: Optional[bool]
        :param embeds: An embed, or list of embeds for the message.
        :type embeds: Optional[Union[Embed, List[Embed]]]
        :param allowed_mentions: The message interactions/mention limits that the message can refer to.
        :type allowed_mentions: Optional[MessageInteraction]
        :param message_reference: The message to "refer" if attempting to reply to a message.
        :type message_reference: Optional[MessageReference]
        :param components: A component, or list of components for the message.
        :type components: Optional[Union[Component, List[Component]]]
        :param sticker_ids: A singular or list of IDs to stickers that the application has access to for the message.
        :type sticker_ids: Optional[Union[str, List[str]]]
        :param type: The type of message response if used for interactions or components.
        :type type: Optional[Union[int, InteractionCallbackType]]
        :param ephemeral: Whether the response is hidden or not.
        :type ephemeral: Optional[bool]
        :return: The sent message as an object.
        :rtype: Message
        """
        _content: str = "" if content is None else content
        _tts: bool = False if tts is None else tts
        # _file = None if file is None else file
        _embeds: list = [] if embeds is None else [embed._json for embed in embeds]
        _allowed_mentions: dict = {} if allowed_mentions is None else allowed_mentions
        _message_reference: dict = {} if message_reference is None else message_reference._json
        _components: list = [{"type": 1, "components": []}]

        if isinstance(components, ActionRow):
            _components[0]["components"] = [component._json for component in components.components]
        elif isinstance(components, (Button, SelectMenu)):
            _components[0]["components"] = [] if components is None else [components._json]
        else:
            _components = [] if components is None else [components]

        _sticker_ids: list = [] if sticker_ids is None else [sticker for sticker in sticker_ids]

        _type: int
        if isinstance(type, InteractionCallbackType):
            _type = (
                InteractionCallbackType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE.value
                if self.deferred
                else InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE.value
            )
        else:
            _type = InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE if type is None else type

        _ephemeral: int = 0 if ephemeral is None else (1 << 6)

        if sticker_ids and len(sticker_ids) > 3:
            raise Exception("Message can only have up to 3 stickers.")

        payload: Message = Message(
            content=_content,
            tts=_tts,
            # file=file,
            embeds=_embeds,
            allowed_mentions=_allowed_mentions,
            message_reference=_message_reference,
            components=_components,
            sticker_ids=_sticker_ids,
            flags=_ephemeral,
        )
        self.message = payload

        async def func():
            if self.responded:
                req = await HTTPClient(interactions.client.cache.token)._post_followup(
                    data=payload._json, token=self.token, application_id=self.application_id
                )
                return req
            else:
                req = await HTTPClient(interactions.client.cache.token).create_interaction_response(
                    token=self.token,
                    application_id=int(self.id),
                    data={"type": _type, "data": payload._json},
                )
                self.responded = True
                return req

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
        sticker_ids: Optional[Union[str, List[str]]] = None,
        type: Optional[int] = None,
        ephemeral: Optional[bool] = None,
    ) -> Message:
        """
        This allows the invocation state described in the "context"
        to send an interaction response. This inherits the arguments
        of the ``.send()`` method.

        :inherit:`interactions.context.InteractionContext.send()`
        :return: The edited message as an object.
        :rtype: Message
        """
        _content: str = "" if content is None else content
        _tts: bool = False if tts is None else tts
        # _file = None if file is None else file
        _embeds: list = [] if embeds is None else [embed._json for embed in embeds]
        _allowed_mentions: dict = {} if allowed_mentions is None else allowed_mentions
        _message_reference: dict = {} if message_reference is None else message_reference._json
        _components: list = [{"type": 1, "components": []}]

        if isinstance(components, ActionRow):
            _components[0]["components"] = [component._json for component in components.components]
        elif isinstance(components, (Button, SelectMenu)):
            _components[0]["components"] = [] if components is None else [components._json]
        else:
            _components = []

        _sticker_ids: list = [] if sticker_ids is None else [sticker for sticker in sticker_ids]
        _type: int = 4 if type is None else type
        _ephemeral: int = 0 if ephemeral is None else (1 << 6)

        if sticker_ids and len(sticker_ids) > 3:
            raise Exception("Message can only have up to 3 stickers.")

        payload: Message = Message(
            content=_content,
            tts=_tts,
            # file=file,
            embeds=_embeds,
            allowed_mentions=_allowed_mentions,
            message_reference=_message_reference,
            components=_components,
            sticker_ids=_sticker_ids,
            flags=_ephemeral,
        )

        async def func():
            req = await HTTPClient(interactions.client.cache.token).edit_interaction_response(
                token=self.token,
                application_id=int(self.id),
                data={"type": _type, "data": payload._json},
                message_id=self.message.id,
            )
            self.message = payload
            self.responded = True
            return req

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
            await HTTPClient(interactions.client.cache.token).delete_webhook_message(
                webhook_id=int(self.id), webhook_token=self.token, message_id=self.message.id
            )
        else:
            # TODO: Wait for Delta to implement an equivocate request method
            # in the HTTPClient for consistency reasons.
            await HTTPClient(interactions.client.cache.token)._req.request(
                Route("DELETE", f"/webhooks/{self.id}/{self.token}/messages/@original")
            )
        self.message = None


class ComponentContext(InteractionContext):
    """
    This is a derivation of the base Context class designed specifically for
    component data.

    :ivar str custom_id: The customized ID for the component to call.
    :ivar typing.Union[str, int, interactions.enums.ComponentType] type: The type of component.
    :ivar list values: The curated list of values under the component. This will be ``None`` if the type is not ``SELECT_MENU``.
    :ivar bool origin: Whether this is the origin of the component.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.responded = False  # remind components that it was not responded to.
