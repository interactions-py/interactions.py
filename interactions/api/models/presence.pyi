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
    url: Optional[str]
    created_at: Snowflake
    timestamps: Optional[PresenceTimestamp]
    application_id: Optional[Snowflake]
    details: Optional[str]
    state: Optional[str]
    emoji: Optional[Emoji]
    party: Optional[PresenceParty]
    assets: Optional[PresenceAssets]
    secrets: Optional[PresenceSecrets]
    instance: Optional[bool]
    flags: Optional[int]
    buttons: Optional[List[PresenceButtons]]
    user: Optional[Any]
    users: Optional[Any]
    status: Optional[Any]
    client_status: Optional[Any]
    activities: Optional[Any]
    sync_id: Optional[Any]
    session_id: Optional[Any]
    id: Optional[Any]
    @property
    def gateway_json(self) -> dict: ...

@define()
class ClientPresence(DictSerializerMixin):
    since: Optional[int]
    activities: Optional[List[PresenceActivity]]
    status: StatusType
    afk: bool
