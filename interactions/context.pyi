from typing import Any, Dict, List, Union

from .api.models.channel import Channel
from .api.models.guild import Guild
from .api.models.member import Member
from .api.models.message import Message
from .api.models.misc import DictSerializerMixin
from .api.models.user import User
from .client import Client
from .enums import ComponentType

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
    __slots__ = ("token", "id", "target", "deferred", "responded", "ephemeral", "resolved", "data")
    token: str
    id: str
    target: str
    deferred: bool
    responded: bool
    ephemeral: bool
    resolved: dict
    data: dict
    def __init__(self, **kwargs) -> None: ...

class ComponentContext(InteractionContext):
    __slots__ = ("custom_id", "type", "values", "origin")
    custom_id: str
    type: Union[str, int, ComponentType]
    values: list
    origin: bool
    def __init__(self, **kwargs) -> None: ...
