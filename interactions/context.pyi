from typing import Any, Dict, List, Optional, Union

from .api.models.channel import Channel
from .api.models.guild import Guild
from .api.models.member import Member
from .api.models.message import Embed, Message, MessageInteraction, MessageReference
from .api.models.misc import DictSerializerMixin
from .api.models.user import User
from .enums import ComponentType, InteractionType
from .models.command import InteractionData
from .models.component import Component

class Context(DictSerializerMixin):
    __slots__ = ("message", "author", "channel", "guild", "args", "kwargs")
    message: Message
    author: Member
    user: User
    channel: Channel
    guild: Guild
    args: List[Any]
    kwargs: Dict[Any, Any]
    def __init__(self, **kwargs) -> None: ...

class InteractionContext(Context):
    __slots__ = (
        "id",
        "application_id",
        "type",
        "data",
        "guild_id",
        "channel_id",
        "token",
        "version",
        "responded",
        "deferred",
    )
    id: str
    application_id: str
    type: Union[str, int, InteractionType]
    data: InteractionData
    guild_id: str
    channel_id: str
    token: str
    version: int = 1
    responded: bool = False
    deferred: bool = False
    def __init__(self, **kwargs) -> None: ...
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
    ) -> Message: ...

class ComponentContext(InteractionContext):
    __slots__ = ("custom_id", "type", "values", "origin")
    custom_id: str
    type: Union[str, int, ComponentType]
    values: list
    origin: bool
    def __init__(self, **kwargs) -> None: ...
