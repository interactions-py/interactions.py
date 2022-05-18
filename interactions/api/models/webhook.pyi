from enum import IntEnum
from .misc import DictSerializerMixin, Snowflake, Image, MISSING, File
from .channel import Channel
from .guild import Guild
from typing import Union, Optional, Any, List
from .user import User
from ..http.client import HTTPClient
from ...client.models.component import Button, SelectMenu, ActionRow
from .message import Message, Embed

class WebhookType(IntEnum):
    Incoming: int
    Channel_Follower: int
    Application: int

class Webhook(DictSerializerMixin):

    _json: dict
    _client: HTTPClient
    id: Snowflake
    type: Union[WebhookType, int]
    guild_id: Optional[Snowflake]
    channel_id: Optional[Snowflake]
    user: Optional[User]
    name: str
    avatar: str
    token: Optional[str]
    application_id: Snowflake
    source_guild: Optional[Guild]
    source_channel: Optional[Channel]
    url: Optional[str]

    def __init__(self, **kwargs): ...
    @classmethod
    async def create(
        cls, client: HTTPClient, channel_id: int, name: str, avatar: Optional[Image] = MISSING
    ) -> "Webhook": ...
    @classmethod
    async def get(cls, client: HTTPClient, webhook_id: int, webhook_token: Optional[str] = MISSING) -> "Webhook": ...
    async def modify(
        self, name: str = MISSING, channel_id: int = MISSING, avatar: Optional[Image] = MISSING
    ) -> "Webhook": ...
    async def execute(
        self,
        content: Optional[str] = MISSING,
        username: Optional[str] = MISSING,
        avatar_url: Optional[str] = MISSING,
        tts: Optional[bool] = MISSING,
        embeds: Optional[Union[Embed, List[Embed]]] = MISSING,
        allowed_mentions: Any = MISSING,
        components: Optional[
            Union[ActionRow, Button, SelectMenu, List[ActionRow], List[Button], List[SelectMenu]]
        ] = MISSING,
        files: Optional[Union[File, List[File]]] = MISSING,
        thread_id: Optional[int] = MISSING,
    ) -> Message: ...
    async def delete(self) -> None: ...
    @property
    def avatar_url(self) -> Optional[str]: ...
