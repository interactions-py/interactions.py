from enum import IntEnum
from .misc import DictSerializerMixin, Snowflake, Image, MISSING
from .channel import Channel
from .guild import Guild
from typing import Union, Optional
from .user import User
from ..http.client import HTTPClient

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
    @property
    def avatar_url(self) -> Optional[str]: ...
