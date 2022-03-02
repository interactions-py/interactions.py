from typing import List, Optional, Union

from ...api.cache import Cache
from ..models.message import Embed, Message
from ..models.misc import Snowflake
from .Request import Request


class HTTPMessage:

    _req: Request
    cache: Cache

    def __init__(self, _req, cache) -> None:
        self._req = _req
        self.cache = cache
    async def send_message(
        self,
        channel_id: Union[int, Snowflake],
        content: str,
        tts: bool = False,
        embeds: Optional[List[Embed]] = None,
        nonce: Union[int, str] = None,
        allowed_mentions=None,  # don't know type
        message_reference: Optional[Message] = None,
    ) -> dict: ...
    async def create_message(self, payload: dict, channel_id: int) -> dict: ...
    async def get_message(self, channel_id: int, message_id: int) -> Optional[dict]: ...
    async def delete_message(
        self, channel_id: int, message_id: int, reason: Optional[str] = None
    ) -> None: ...
    async def delete_messages(
            self, channel_id: int, message_ids: List[int], reason: Optional[str] = None
    ) -> None: ...
    async def edit_message(self, channel_id: int, message_id: int, payload: dict) -> dict: ...
    async def pin_message(self, channel_id: int, message_id: int) -> None: ...
    async def unpin_message(self, channel_id: int, message_id: int) -> None: ...
    async def publish_message(self, channel_id: int, message_id: int) -> dict: ...
