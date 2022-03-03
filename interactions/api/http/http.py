from typing import Any, Optional, Tuple

import interactions.api.cache

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
    """
    The user-facing client of the Web API for individual endpoints.

    :ivar str token: The token of the application.
    :ivar Request _req: The requesting interface for endpoints.
    :ivar Cache cache: The referenced cache.
    """

    __slots__ = (
        "token",
        "_req",
        "cache",
    )

    token: str
    _req: _Request
    cache: Cache

    def __init__(self, token: str):
        self.token = token
        self._req = _Request(self.token)
        self.cache = interactions.api.cache.ref_cache
        _UserRequest.__init__(self)
        _MessageRequest.__init__(self)
        _GuildRequest.__init__(self)
        _ChannelRequest.__init__(self)
        _ThreadRequest.__init__(self)
        _ReactionRequest.__init__(self)
        _StickerRequest.__init__(self)
        _InteractionRequest.__init__(self)
        _WebhookRequest.__init__(self)
        _ScheduledEventRequest.__init__(self)
        _EmojiRequest.__init__(self)
        _MemberRequest.__init__(self)

        # An ideology is that this client does every single HTTP call, which reduces multiple ClientSessions in theory
        # because of how they are constructed/closed. This includes Gateway

    async def get_gateway(self) -> str:
        """This calls the Gateway endpoint and returns a v9 gateway link with JSON encoding."""

        url: Any = await self._req.request(
            Route("GET", "/gateway")
        )  # typehinting Any because pycharm yells
        return f'{url["url"]}?v=10&encoding=json'

    async def get_bot_gateway(self) -> Tuple[int, str]:
        """
        This calls the BOT Gateway endpoint.

        :return: A tuple denoting (shard, gateway_url), url from API v9 and JSON encoding
        """

        data: Any = await self._req.request(Route("GET", "/gateway/bot"))
        return data["shards"], f'{data["url"]}?v=9&encoding=json'

    async def login(self) -> Optional[dict]:
        """
        This 'logins' to the gateway, which makes it available to use any other endpoint.
        """

        return await self._req.request(
            Route("GET", "/users/@me")
        )  # Internally raises any Exception.

    async def logout(self) -> None:
        """This 'log outs' the session."""

        await self._req.request(Route("POST", "/auth/logout"))

    @property
    def req(self) -> _Request:
        return self._req

    # ---- Oauth2 endpoint

    async def get_current_bot_information(self) -> dict:
        """
        Returns the bot user application object without flags.
        """
        return await self._req.request(Route("GET", "/oauth2/applications/@me"))

    async def get_current_authorisation_information(self) -> dict:
        """
        Returns info about the current authorization of the bot user
        """
        return await self._req.request(Route("GET", "/oauth2/@me"))
