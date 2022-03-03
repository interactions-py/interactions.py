from typing import Optional, Tuple

from .request import _Request
from ...api.cache import Cache
from .user import _UserRequest
from .message import _MessageRequest
from .guild import _GuildRequest
from .channel import _ChannelRequest
from .thread import _ThreadRequest
from .sticker import _StickerRequest
from .reaction import _ReactionRequest
from .webhook import _WebhookRequest
from .emoji import _EmojiRequest
from .scheduledEvent import _ScheduledEventRequest
from .interaction import _InteractionRequest
from .member import _MemberRequest

class HTTPClient:
    token: str
    _req: _Request
    cache: Cache

    message: _MessageRequest
    user: _UserRequest
    guild: _GuildRequest
    channel: _ChannelRequest
    member: _MemberRequest
    thread: _ThreadRequest
    reaction: _ReactionRequest
    sticker: _StickerRequest
    interaction: _InteractionRequest
    webhook: _WebhookRequest
    emoji: _EmojiRequest
    scheduled_event: _ScheduledEventRequest

    def __init__(self, token: str): ...

    async def get_gateway(self) -> str: ...
    async def get_bot_gateway(self) -> Tuple[int, str]: ...
    async def login(self) -> Optional[dict]: ...
    async def logout(self) -> None: ...
    @property
    def req(self) -> _Request: ...
    async def get_current_bot_information(self) -> dict: ...
    async def get_current_authorisation_information(self) -> dict: ...
