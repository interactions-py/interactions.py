# from io import FileIO
from typing import List, Optional, Union

import interactions.client

from .api.http import HTTPClient
from .api.models.message import Embed, Message, MessageInteraction, MessageReference
from .api.models.misc import DictSerializerMixin
from .models.component import Component


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

    async def send(
        self,
        content: Optional[str] = None,
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

        ok he kinda work now
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
            flags:_flags
        )
        self.message = payload

        async def func():
            req = await HTTPClient(interactions.client.cache.token).create_interaction_response(
                token=self.token,
                application_id=int(self.id),
                data={"type": _type, "data": payload._json},
            )
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
