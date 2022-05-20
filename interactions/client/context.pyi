from ..api import InteractionException as InteractionException
from ..api.models.channel import Channel as Channel
from ..api.models.guild import Guild as Guild
from ..api.models.member import Member as Member
from ..api.models.message import Embed as Embed, Message as Message, MessageInteraction as MessageInteraction, MessageReference as MessageReference
from ..api.models.misc import DictSerializerMixin as DictSerializerMixin, MISSING as MISSING, Snowflake as Snowflake, define as define, field as field
from ..api.models.user import User as User
from ..base import get_logger as get_logger
from ..ext import converter as converter
from .enums import InteractionCallbackType as InteractionCallbackType, InteractionType as InteractionType
from .models.command import Choice as Choice
from .models.component import ActionRow as ActionRow, Button as Button, Modal as Modal, SelectMenu as SelectMenu
from .models.misc import InteractionData as InteractionData
from logging import Logger
from typing import Any, List, Optional, Union

log: Logger

class _Context(DictSerializerMixin):
    client: Any
    message: Optional[Message]
    author: Member
    member: Member
    user: User
    channel: Optional[Channel]
    guild: Optional[Guild]
    id: Snowflake
    application_id: Snowflake
    type: InteractionType
    callback: Optional[InteractionCallbackType]
    data: InteractionData
    version: int
    token: str
    guild_id: Snowflake
    channel_id: Snowflake
    responded: bool
    deferred: bool
    def __attrs_post_init__(self) -> None: ...
    async def get_channel(self) -> Channel: ...
    async def get_guild(self) -> Guild: ...
    async def send(self, content: Optional[str] = ..., *, tts: Optional[bool] = ..., embeds: Optional[Union[Embed, List[Embed]]] = ..., allowed_mentions: Optional[MessageInteraction] = ..., components: Optional[Union[ActionRow, Button, SelectMenu, List[ActionRow], List[Button], List[SelectMenu]]] = ..., ephemeral: Optional[bool] = ...) -> dict: ...
    async def edit(self, content: Optional[str] = ..., *, tts: Optional[bool] = ..., embeds: Optional[Union[Embed, List[Embed]]] = ..., allowed_mentions: Optional[MessageInteraction] = ..., message_reference: Optional[MessageReference] = ..., components: Optional[Union[ActionRow, Button, SelectMenu, List[ActionRow], List[Button], List[SelectMenu]]] = ...) -> Message: ...
    async def popup(self, modal: Modal) -> None: ...

class CommandContext(_Context):
    target: Optional[Union[Message, Member, User]]
    def __attrs_post_init__(self) -> None: ...
    message: Any
    async def edit(self, content: Optional[str] = ..., **kwargs) -> Message: ...
    deferred: bool
    callback: Any
    async def defer(self, ephemeral: Optional[bool] = ...) -> None: ...
    responded: bool
    async def send(self, content: Optional[str] = ..., **kwargs) -> Message: ...
    async def delete(self) -> None: ...
    async def populate(self, choices: Union[Choice, List[Choice]]) -> List[Choice]: ...

class ComponentContext(_Context):
    callback: Any
    message: Any
    responded: bool
    async def edit(self, content: Optional[str] = ..., **kwargs) -> Message: ...
    async def send(self, content: Optional[str] = ..., **kwargs) -> Message: ...
    deferred: bool
    async def defer(self, ephemeral: Optional[bool] = ..., edit_origin: Optional[bool] = ...) -> None: ...
    @property
    def custom_id(self) -> Optional[str]: ...
    @property
    def label(self) -> Optional[str]: ...
