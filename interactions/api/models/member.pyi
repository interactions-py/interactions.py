from datetime import datetime
from typing import Any, List, Optional, Union

from .misc import DictSerializerMixin, MISSING, Snowflake
from .role import Role
from .user import User
from .flags import Permissions
from ..http import HTTPClient
from .message import Message, Embed, MessageInteraction
from ...models.component import ActionRow, Button, SelectMenu

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
    permissions: Optional[Permissions]
    communication_disabled_until: Optional[datetime.isoformat]
    hoisted_role: Any  # TODO: post-v4: Investigate what this is for when documented by Discord.
    def __init__(self, **kwargs): ...
    @classmethod
    async def fetch(
        cls, guild_id: int, member_id: int, *, cache: Optional[bool] = True, http: HTTPClient
    ) -> "Member": ...
    @property
    def mention(self) -> str: ...
    def id(self) -> Snowflake: ...
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
        content: Optional[str] = MISSING,
        *,
        components: Optional[
            Union[
                ActionRow,
                Button,
                SelectMenu,
                List[ActionRow],
                List[Button],
                List[SelectMenu],
            ]
        ] = MISSING,
        tts: Optional[bool] = MISSING,
        # attachments: Optional[List[Any]] = None,  # TODO: post-v4: Replace with own file type.
        embeds: Optional[Union[Embed, List["Embed"]]] = MISSING,
        allowed_mentions: Optional[MessageInteraction] = MISSING,
    ) -> Message: ...
    async def modify(
        self,
        guild_id: int,
        nick: Optional[str] = MISSING,
        roles: Optional[List[int]] = MISSING,
        mute: Optional[bool] = MISSING,
        deaf: Optional[bool] = MISSING,
        channel_id: Optional[int] = MISSING,
        communication_disabled_until: Optional[datetime.isoformat] = MISSING,
        reason: Optional[str] = None,
    ) -> "Member": ...
    async def add_to_thread(
        self,
        thread_id: int,
    ) -> None: ...
