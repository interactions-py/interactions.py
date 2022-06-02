from enum import IntEnum
from typing import Any, List, Optional, Union

from .attrs_utils import ClientSerializerMixin, MISSING, define
from .channel import Channel
from .guild import Guild
from .message import Embed, Message
from .misc import File, Image, Snowflake
from .user import User
from ..http.client import HTTPClient
from ...client.models.component import ActionRow, Button, SelectMenu


class WebhookType(IntEnum):
    Incoming: int
    Channel_Follower: int
    Application: int


@define()
class Webhook(ClientSerializerMixin):
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

    def __attrs_post_init__(self): ...

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
    ) -> Optional[Message]: ...
    async def delete(self) -> None: ...
    @property
    def avatar_url(self) -> Optional[str]: ...
