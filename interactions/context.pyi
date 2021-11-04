from typing import Any, Dict, List, Union

from .api.models.channel import Channel
from .api.models.guild import Guild
from .api.models.member import Member
from .api.models.message import Message
from .api.models.misc import DictSerializerMixin
from .api.models.user import User
from .enums import ComponentType, InteractionType
from .models.command import InteractionData

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
    def __init__(self, **kwargs) -> None: ...

class ComponentContext(InteractionContext):
    __slots__ = ("custom_id", "type", "values", "origin")
    custom_id: str
    type: Union[str, int, ComponentType]
    values: list
    origin: bool
    def __init__(self, **kwargs) -> None: ...
