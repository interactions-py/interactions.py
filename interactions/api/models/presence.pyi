from enum import IntEnum
from typing import Any, List, Optional

from ..models import StatusType as StatusType
from ..models.message import Emoji as Emoji
from .attrs_utils import DictSerializerMixin, define
from .misc import Snowflake

@define()
class PresenceParty(DictSerializerMixin):
    id: Optional[Snowflake]
    size: Optional[List[int]]

@define()
class PresenceAssets(DictSerializerMixin):
    large_image: Optional[str]
    large_text: Optional[str]
    small_image: Optional[str]
    small_text: Optional[str]

@define()
class PresenceSecrets(DictSerializerMixin):
    join: Optional[str]
    spectate: Optional[str]
    match: Optional[str]

@define()
class PresenceButtons(DictSerializerMixin):
    label: str
    url: str

@define()
class PresenceTimestamp(DictSerializerMixin):
    start: Optional[int]
    end: Optional[int]

class PresenceActivityType(IntEnum):
    GAME: int
    STREAMING: int
    LISTENING: int
    WATCHING: int
    CUSTOM: int
    COMPETING: int

@define()
class PresenceActivity(DictSerializerMixin):
    name: str
    type: PresenceActivityType
    url: Optional[str] = None
    created_at: int = 0
    timestamps: Optional[PresenceTimestamp] = None
    application_id: Optional[Snowflake] = None
    details: Optional[str] = None
    state: Optional[str] = None
    emoji: Optional[Emoji] = None
    party: Optional[PresenceParty] = None
    assets: Optional[PresenceAssets] = None
    secrets: Optional[PresenceSecrets] = None
    instance: Optional[bool] = None
    flags: Optional[int] = None
    buttons: Optional[List[PresenceButtons]] = None
    user: Optional[Any] = None
    users: Optional[Any] = None
    status: Optional[Any] = None
    client_status: Optional[Any] = None
    activities: Optional[Any] = None
    sync_id: Optional[Any] = None
    session_id: Optional[Any] = None
    id: Optional[Any] = None
    @property
    def gateway_json(self) -> dict: ...

@define()
class ClientPresence(DictSerializerMixin):
    since: Optional[int] = None
    activities: Optional[List[PresenceActivity]] = None
    status: StatusType
    afk: bool = False
