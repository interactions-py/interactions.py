from typing import Any, List, Optional

from ...api.cache import Cache
from .request import _Request


class WebhookRequest:

    _req: _Request
    cache: Cache

    def __init__(self) -> None: ...
    async def create_webhook(self, channel_id: int, name: str, avatar: Any = None) -> dict: ...
    async def get_channel_webhooks(self, channel_id: int) -> List[dict]: ...
    async def get_guild_webhooks(self, guild_id: int) -> List[dict]: ...
    async def get_webhook(self, webhook_id: int, webhook_token: str = None) -> dict: ...
    async def modify_webhook(
        self,
        webhook_id: int,
        name: str,
        avatar: Any,
        channel_id: int,
        webhook_token: str = None,
    ) -> dict: ...
    async def delete_webhook(self, webhook_id: int, webhook_token: str = None): ...
    async def execute_webhook(
        self,
        webhook_id: int,
        webhook_token: str,
        payload: dict,
        wait: bool = False,
        thread_id: Optional[int] = None,
    ) -> Optional[dict]: ...
    async def execute_slack_webhook(
        self, webhook_id: int, webhook_token: str, payload: dict
    ) -> None: ...
    async def execute_github_webhook(
        self, webhook_id: int, webhook_token: str, payload: dict
    ) -> None: ...
    async def get_webhook_message(
        self, webhook_id: int, webhook_token: str, message_id: int
    ) -> dict: ...
    async def edit_webhook_message(
        self, webhook_id: int, webhook_token: str, message_id: int, data: dict
    ) -> dict: ...
    async def delete_webhook_message(
        self, webhook_id: int, webhook_token: str, message_id: int
    ) -> None: ...
    async def delete_original_webhook_message(self, webhook_id: int, webhook_token: str) -> None: ...
