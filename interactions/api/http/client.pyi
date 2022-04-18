from typing import Optional, Tuple

from .request import _Request
from ...api.cache import Cache
from .channel import _ChannelRequest
from .emoji import _EmojiRequest
from .guild import _GuildRequest
from .interaction import _InteractionRequest
from .member import _MemberRequest
from .message import _MessageRequest
from .reaction import _ReactionRequest
from .request import _Request
from .route import Route
from .scheduledEvent import _ScheduledEventRequest
from .sticker import _StickerRequest
from .thread import _ThreadRequest
from .user import _UserRequest
from .webhook import _WebhookRequest


class HTTPClient(
    _ChannelRequest,
    _EmojiRequest,
    _GuildRequest,
    _InteractionRequest,
    _MemberRequest,
    _MessageRequest,
    _ReactionRequest,
    _ScheduledEventRequest,
    _StickerRequest,
    _ThreadRequest,
    _UserRequest,
    _WebhookRequest,
):

    token: str
    _req: _Request
    cache: Cache

    def __init__(self, token: str): ...

    async def get_gateway(self) -> str: ...
    async def get_bot_gateway(self) -> Tuple[int, str]: ...
    async def login(self) -> Optional[dict]: ...
    async def logout(self) -> None: ...
    @property
    def req(self) -> _Request: ...
    async def get_current_bot_information(self) -> dict: ...
    async def get_current_authorisation_information(self) -> dict: ...
