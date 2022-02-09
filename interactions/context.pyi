from logging import Logger
from typing import Any, List, Optional, Union

from .api import HTTPClient
from .api.models.channel import Channel as Channel
from .api.models.guild import Guild as Guild
from .api.models.member import Member as Member
from .api.models.message import Embed as Embed
from .api.models.message import Message as Message
from .api.models.message import MessageInteraction as MessageInteraction
from .api.models.message import MessageReference as MessageReference
from .api.models.misc import MISSING as MISSING
from .api.models.misc import DictSerializerMixin as DictSerializerMixin
from .api.models.misc import Snowflake as Snowflake
from .api.models.user import User as User
from .base import get_logger as get_logger
from .enums import InteractionCallbackType as InteractionCallbackType
from .enums import InteractionType as InteractionType
from .models.command import Choice as Choice
from .models.component import ActionRow as ActionRow
from .models.component import Button as Button
from .models.component import Modal as Modal
from .models.component import SelectMenu as SelectMenu
from .models.misc import InteractionData as InteractionData

class ContextMixin(DictSerializerMixin):
    message: Optional[Message]
    author: Member
    member: Member
    user: User
    channel: Optional[Channel]
    guild: Optional[Guild]
    client: HTTPClient
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
    def __init__(self, **kwargs) -> None: ...
    async def get_channel(self) -> Channel: ...
    async def get_guild(self) -> Guild: ...
    async def send(
        self,
        content: Optional[str] = ...,
        *,
        tts: Optional[bool] = ...,
        embeds: Optional[Union[Embed, List[Embed]]] = ...,
        allowed_mentions: Optional[MessageInteraction] = ...,
        components: Optional[
            Union[ActionRow, Button, SelectMenu, List[ActionRow], List[Button], List[SelectMenu]]
        ] = ...,
        ephemeral: Optional[bool] = ...
    ) -> Message: ...
    async def edit(
        self,
        content: Optional[str] = ...,
        *,
        tts: Optional[bool] = ...,
        embeds: Optional[Union[Embed, List[Embed]]] = ...,
        allowed_mentions: Optional[MessageInteraction] = ...,
        message_reference: Optional[MessageReference] = ...,
        components: Optional[
            Union[ActionRow, Button, SelectMenu, List[ActionRow], List[Button], List[SelectMenu]]
        ] = ...
    ) -> Message: ...
    async def popup(self, modal: Modal) -> None: ...

class CommandContext(ContextMixin):
    target: Optional[Union[Message, Member, User]]
    def __init__(self, **kwargs) -> None: ...
    async def edit(self, content: Optional[str] = ..., **kwargs) -> Message: ...
    async def defer(self, ephemeral: Optional[bool] = ...) -> None: ...
    async def send(self, content: str = ..., **kwargs): ...
    async def delete(self) -> None: ...
    async def populate(self, choices: Union[Choice, List[Choice]]) -> List[Choice]: ...

class ComponentContext(ContextMixin):
    def __init__(self, **kwargs) -> None: ...
    async def edit(self, content: Optional[str] = ..., **kwargs) -> Message: ...
    async def send(self, content: str = ..., **kwargs): ...
    async def defer(
        self, ephemeral: Optional[bool] = ..., edit_origin: Optional[bool] = ...
    ) -> None: ...
