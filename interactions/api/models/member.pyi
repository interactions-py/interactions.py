from datetime import datetime
from typing import Any, List, Optional, Union

from .misc import DictSerializerMixin
from .role import Role
from .user import User
from ..http import HTTPClient
from .message import Message

class Member(DictSerializerMixin):

    _json: dict
    _client: HTTPClient
    user: Optional[User]
    nick: Optional[str]
    avatar: Optional[str]
    roles: List[Role]
    joined_at: datetime
    premium_since: datetime
    deaf: bool
    mute: bool
    is_pending: Optional[bool]
    pending: Optional[bool]
    permissions: Optional[str]
    communication_disabled_until: Optional[datetime.isoformat]
    hoisted_role: Any  # TODO: post-v4: Investigate what this is for when documented by Discord.
    def __init__(self, **kwargs): ...
    async def ban(
        self,
        guild_id: int,
        reason: Optional[str] = None,
        delete_message_days: Optional[int] = 0,
    ) -> None: ...
    async def kick(
        self,
        guild_id: int,
        reason: Optional[str] = None,
    ) -> None: ...
    async def add_role(
        self,
        role: Union[Role, int],
        guild_id: int,
        reason: Optional[str],
    ) -> None: ...
    async def remove_role(
        self,
        role: Union[Role, int],
        guild_id: int,
        reason: Optional[str],
    ) -> None: ...
    async def send(
        self,
        content: Optional[str] = None,
        *,
        tts: Optional[bool] = False,
        # attachments: Optional[List[Any]] = None,  # TODO: post-v4: Replace with own file type.
        embeds=None,
        allowed_mentions=None,
    ) -> Message: ...
    async def modify(
        self,
        guild_id: int,
        nick: Optional[str] = None,
        roles: Optional[List[int]] = None,
        mute: Optional[bool] = None,
        deaf: Optional[bool] = None,
        channel_id: Optional[int] = None,
        communication_disabled_until: Optional[datetime.isoformat] = None,
        reason: Optional[str] = None,
    ) -> "Member": ...
    async def add_to_thread(
        self,
        thread_id: int,
    ) -> None: ...
