from typing import Union

from .api.models.channel import CategoryChannel, DMChannel, TextChannel, VoiceChannel
from .api.models.guild import Guild
from .api.models.member import Member
from .api.models.message import Message
from .api.models.user import User
from .client import Client
from .enums import ComponentType

class Context:
    __slots__ = ("client", "message", "author", "channel", "guild", "args", "kwargs")
    client: Client
    message: Message
    author: Union[Member, User]
    channel: Union[CategoryChannel, TextChannel, VoiceChannel, DMChannel]
    guild: Guild
    args: list
    kwargs: dict

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

class ComponentContext(InteractionContext):
    __slots__ = ("custom_id", "type", "values", "origin")
    custom_id: str
    type: Union[str, int, ComponentType]
    values: list
    origin: bool
