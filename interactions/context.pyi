from typing import List, Optional, Union

from .api.http import HTTPClient
from .api.models.channel import Channel
from .api.models.guild import Guild
from .api.models.member import Member
from .api.models.message import Embed, Message, MessageInteraction, MessageReference
from .api.models.misc import DictSerializerMixin, Snowflake
from .api.models.user import User
from .enums import ComponentType, InteractionType
from .models.command import Choice, Option
from .models.component import ActionRow, Button, Component, Modal, SelectMenu
from .models.misc import InteractionData

class Context(DictSerializerMixin):
    message: Optional[Message]
    author: Member
    member: Member
    user: User
    channel: Channel
    guild: Guild
    client: HTTPClient
    def __init__(self, **kwargs) -> None: ...

class CommandContext(Context):
    id: Snowflake
    application_id: Snowflake
    custom_id: str
    type: InteractionType
    data: InteractionData
    target: Optional[Union[Message, Member, User]]
    version: int
    token: str
    guild_id: Snowflake
    channel_id: Snowflake
    responded: bool
    deferred: bool
    def __init__(self, **kwargs) -> None: ...
    async def defer(self, ephemeral: Optional[bool] = None) -> None: ...
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
    async def edit(
        self,
        content: Optional[str] = None,
        *,
        tts: Optional[bool] = None,
        # file: Optional[FileIO] = None,
        embeds: Optional[Union[Embed, List[Embed]]] = None,
        allowed_mentions: Optional[MessageInteraction] = None,
        message_reference: Optional[MessageReference] = None,
        components: Optional[Union[ActionRow, Button, SelectMenu]] = None,
    ) -> Message: ...
    async def delete(self) -> None: ...
    async def popup(self, modal: Modal): ...
    async def populate(self, choices: Union[Choice, List[Choice]]) -> List[Choice]: ...

class ComponentContext(CommandContext):
    type: ComponentType
    def __init__(self, **kwargs) -> None: ...
