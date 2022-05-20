from ...ext import converter as converter
from ..models import StatusType as StatusType
from ..models.message import Emoji as Emoji
from .misc import DictSerializerMixin as DictSerializerMixin, Snowflake as Snowflake, convert_list as convert_list, define as define, field as field
from enum import IntEnum
from typing import Any, List, Optional

class PresenceParty(DictSerializerMixin):
    id: Optional[Snowflake]
    size: Optional[List[int]]

class PresenceAssets(DictSerializerMixin):
    large_image: Optional[str]
    large_text: Optional[str]
    small_image: Optional[str]
    small_text: Optional[str]

class PresenceSecrets(DictSerializerMixin):
    join: Optional[str]
    spectate: Optional[str]
    match: Optional[str]

class PresenceButtons(DictSerializerMixin):
    label: str
    url: str

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

class ClientPresence(DictSerializerMixin):
    since: Optional[int]
    activities: Optional[List[PresenceActivity]]
    status: StatusType
    afk: bool
