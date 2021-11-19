from typing import Any, Dict, List, Optional, Union

from .api.models.channel import Channel
from .api.models.guild import Guild
from .api.models.member import Member
from .api.models.message import Embed, Message, MessageInteraction, MessageReference
from .api.models.misc import DictSerializerMixin
from .api.models.user import User
from .enums import ComponentType, InteractionType
from .models import InteractionData
from .models.component import Component

class Context(DictSerializerMixin):
    message: Message
    author: Member
    user: User
    channel: Channel
    guild: Guild
    args: List[Any]
    kwargs: Dict[Any, Any]
    __slots__ = ("message", "author", "channel", "user", "guild", "args", "kwargs")
    def __init__(self, **kwargs) -> None: ...

class InteractionContext(Context):
    id: str
    application_id: str
    type: Union[str, int, InteractionType]
    data: InteractionData
    guild_id: str
    channel_id: str
    token: str
    responded: bool
    __slots__ = (
        "message",
        "author",
        "channel",
        "user",
        "guild",
        "args",
        "kwargs",
        "id",
        "application_id",
        "type",
        "data",
        "guild_id",
        "channel_id",
        "token",
        "responded",
    )
    def __init__(self, **kwargs) -> None: ...
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
    ) -> Message: ...

class ComponentContext(InteractionContext):
    custom_id: str
    type: Union[str, int, ComponentType]
    values: list
    origin: bool
    __slots__ = (
        "message",
        "author",
        "channel",
        "user",
        "guild",
        "args",
        "kwargs",
        "id",
        "application_id",
        "type",
        "data",
        "guild_id",
        "channel_id",
        "token",
        "responded",
        "custom_id",
        "type",
        "values",
        "origin",
    )
    def __init__(self, **kwargs) -> None: ...
