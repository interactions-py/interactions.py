from typing import TYPE_CHECKING, Any, List, Optional, Tuple

from .channel import ChannelRequest
from .emoji import EmojiRequest
from .guild import GuildRequest
from .interaction import InteractionRequest
from .invite import InviteRequest
from .member import MemberRequest
from .message import MessageRequest
from .reaction import ReactionRequest
from .request import _Request
from .route import Route
from .scheduledEvent import ScheduledEventRequest
from .sticker import StickerRequest
from .thread import ThreadRequest
from .user import UserRequest
from .webhook import WebhookRequest

if TYPE_CHECKING:
    from ...api.cache import Cache

__all__ = ("HTTPClient",)


class HTTPClient(
    ChannelRequest,
    EmojiRequest,
    GuildRequest,
    InteractionRequest,
    InviteRequest,
    MemberRequest,
    MessageRequest,
    ReactionRequest,
    ScheduledEventRequest,
    StickerRequest,
    ThreadRequest,
    UserRequest,
    WebhookRequest,
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
    cache: "Cache"

    def __init__(self, token: str, cache: "Cache"):  # noqa skip the no super imports
        self.token = token
        self._req = _Request(self.token)
        self.cache = cache

        # An ideology is that this client does every single HTTP call, which reduces multiple ClientSessions in theory
        # because of how they are constructed/closed. This includes Gateway

    async def get_gateway(self) -> str:
        """This calls the Gateway endpoint and returns a v9 gateway link with JSON encoding."""

        url: Any = await self._req.request(
            Route("GET", "/gateway")
        )  # typehinting Any because pycharm yells
        try:
            _url = f'{url["url"]}?v=10&encoding=json&compress=zlib-stream'
        except TypeError:  # seen a few times
            _url = "wss://gateway.discord.gg?v=10&encoding=json&compress=zlib-stream"
        return _url

    async def get_bot_gateway(self) -> Tuple[int, str]:
        """
        This calls the BOT Gateway endpoint.

        :return: A tuple denoting (shard, gateway_url), url from API v9 and JSON encoding
        """

        data: Any = await self._req.request(Route("GET", "/gateway/bot"))
        try:
            _url = f'{data["url"]}?v=10&encoding=json&compress=zlib-stream'
        except TypeError:  # seen a few times
            _url = "wss://gateway.discord.gg?v=10&encoding=json&compress=zlib-stream"
        return data["shards"], _url

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

    # ---- Role connection metadata endpoints

    async def get_application_role_connection_metadata(self, application_id: int) -> List[dict]:
        """
        Returns a list of application role connection metadata objects for an application.
        """
        return await self._req.request(
            Route("GET", f"/applications/{application_id}/role-connections/metadata")
        )

    async def update_application_role_connection_metadata(
        self, application_id: int, payload: List[dict]
    ) -> List[dict]:
        """
        Updates and returns a list of application role connection metadata objects for an application.

        .. note:: The maximum metadata objects supported via the API is five.
        """
        return await self._req.request(
            Route("PUT", f"/applications/{application_id}/role-connections/metadata"), json=payload
        )
