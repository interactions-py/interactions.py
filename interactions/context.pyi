from typing import Any, Dict, List, Optional, Union

from . import Component
from .api.models.channel import Channel
from .api.models.guild import Guild
from .api.models.member import Member
from .api.models.message import Embed, Message, MessageInteraction, MessageReference
from .api.models.misc import DictSerializerMixin
from .api.models.user import User
from .enums import ComponentType, InteractionType
from .models.command import InteractionData

class Context(DictSerializerMixin):
    message: Message
    author: Member
    user: User
    channel: Channel
    guild: Guild
    args: List[Any]
    kwargs: Dict[Any, Any]
    def __init__(self, **kwargs) -> None: ...

class InteractionContext(Context):
    id: str
    application_id: str
    type: Union[str, int, InteractionType]
    data: InteractionData
    guild_id: str
    channel_id: str
    token: str
    version: int = 1
    def __init__(self, **kwargs) -> None: ...
    async def send(
        self,
        content: Optional[str],
        tts: Optional[bool],
        embeds: Optional[Union[Embed, List[Embed]]],
        allowed_mentions: Optional[MessageInteraction],
        message_reference: Optional[MessageReference],
        components: Optional[Union[Component, List[Component]]],
        sticker_ids: Optional[Union[str, List[str]]],
        type: Optional[int],
    ) -> Message: ...

class ComponentContext(InteractionContext):
    custom_id: str
    type: Union[str, int, ComponentType]
    values: list
    origin: bool
    def __init__(self, **kwargs) -> None: ...
