from typing import Optional, Tuple

from ...api.cache import Cache
from .channel import ChannelRequest
from .emoji import EmojiRequest
from .guild import GuildRequest
from .interaction import InteractionRequest
from .member import MemberRequest
from .message import MessageRequest
from .reaction import ReactionRequest
from .request import _Request
from .scheduledEvent import ScheduledEventRequest
from .sticker import StickerRequest
from .thread import ThreadRequest
from .user import UserRequest
from .webhook import WebhookRequest


class HTTPClient(
    ChannelRequest,
    EmojiRequest,
    GuildRequest,
    InteractionRequest,
    MemberRequest,
    MessageRequest,
    ReactionRequest,
    ScheduledEventRequest,
    StickerRequest,
    ThreadRequest,
    UserRequest,
    WebhookRequest,
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
