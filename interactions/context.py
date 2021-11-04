# from io import FileIO
from typing import List, Optional, Union

import interactions.client

from .api.http import HTTPClient
from .api.models.channel import Channel
from .api.models.member import Member
from .api.models.message import Embed, Message, MessageInteraction, MessageReference
from .api.models.misc import DictSerializerMixin
from .api.models.user import User
from .enums import InteractionType
from .models.component import Component
from .models.misc import InteractionData


class Context(DictSerializerMixin):
    r"""
    The base class of \"context\" for dispatched event data
    from the gateway.

    :ivar interactions.api.models.message.Message message: The message data model.
    :ivar interactions.api.models.member.Member author: The member data model.
    :ivar interactions.api.models.user.User user: The user data model.
    :ivar interactions.api.models.channel.Channel channel: The channel data model.
    :ivar interactions.api.models.guild.Guild guild: The guild data model.
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
    :ivar typing.Union[str, int, interactions.enums.InteractionType] type: The type of interaction.
    :ivar interactions.models.misc.InteractionData data: The application command data.
    :ivar str guild_id: The guild ID the interaction falls under.
    :ivar str channel_id: The channel ID the interaction was instantiated from.
    :ivar str token: The token of the interaction response.
    :ivar int=1 version: The version of interaction creation. Always defaults to ``1``.
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

    async def send(
        self,
        content: Optional[str] = None,
        *,
        tts: Optional[bool] = None,
        # file: Optional[FileIO] = None,
        embeds: Optional[Union[Embed, List[Embed]]] = None,
        allowed_mentions: Optional[MessageInteraction] = None,
        message_reference: Optional[MessageReference] = None,
        components: Optional[Union[Component, List[Component]]] = None,
        sticker_ids: Optional[Union[str, List[str]]] = None,
        type: Optional[int] = None,
        flags: Optional[int] = None,
    ) -> Message:
        """
        A **very** primitive form of the send model to get the uttermost
        basic implementation of command responses up and running.

        :param content: The contents of the message as a string or string-converted value.
        :type content: typing.Optional[str]
        :param tts: Whether the message utilizes the text-to-speech Discord programme or not.
        :type tts: typing.Optional[bool]
        :param embeds: An embed, or list of embeds for the message.
        :type embeds: typing.Optional[typing.Union[interactions.api.models.message.Embed, typing.List[interactions.api.models.message.Embed]]]
        :param allowed_mentions: The message interactions/mention limits that the message can refer to.
        :type allowed_mentions: typing.Optional[interactions.api.models.message.MessageInteraction]
        :param message_reference: The message to "refer" if attempting to reply to a message.
        :type message_reference: typing.Optional[interactions.api.models.message.MessageReference]
        :param components: A component, or list of components for the message.
        :type components: typing.Optional[typing.Union[interactions.models.component.Component, typing.List[interactions.models.component.Component]]]
        :param sticker_ids: A singular or list of IDs to stickers that the application has access to for the message.
        :type sticker_ids: typing.Optional[typing.Union[str, typing.List[str]]]
        :param type: The type of message response if used for interactions.
        :type type: typing.Optional[int]
        :param flags: The flags of the message if used for interactions.
        :type flags: typing.Optional[int]
        :return: interactions.api.models.message.Message
        """
        _content: str = "" if content is None else content
        _tts: bool = False if tts is None else tts
        # _file = None if file is None else file
        _embeds: list = [] if embeds is None else [embed._json for embed in embeds]
        _allowed_mentions: dict = {} if allowed_mentions is None else allowed_mentions
        _message_reference: dict = {} if message_reference is None else message_reference._json
        _components: list = (
            [] if components is None else [component._json for component in components]
        )
        _sticker_ids: list = [] if sticker_ids is None else [sticker for sticker in sticker_ids]
        _type: int = 4 if type is None else type
        _flags: int = 0 if flags is None else flags

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
            flags=_flags,
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
