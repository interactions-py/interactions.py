from typing import List, Optional

from .message import Emoji
from .misc import DictSerializerMixin, Snowflake

class PresenceParty(DictSerializerMixin):
    _json: dict
    id: Optional[Snowflake]
    size: Optional[List[int]]
    def __init__(self, **kwargs): ...

class PresenceAssets(DictSerializerMixin):
    _json: dict
    large_image: Optional[str]
    large_text: Optional[str]
    small_image: Optional[str]
    small_text: Optional[str]
    def __init__(self, **kwargs): ...

class PresenceSecrets(DictSerializerMixin):
    _json: dict
    join: Optional[str]
    spectate: Optional[str]
    match: Optional[str]
    def __init__(self, **kwargs): ...

class PresenceButtons(DictSerializerMixin):
    _json: dict
    label: str
    url: str
    def __init__(self, **kwargs): ...

class PresenceTimestamp(DictSerializerMixin):
    _json: dict
    start: Optional[int]
    end: Optional[int]
    def __init__(self, **kwargs): ...

class PresenceActivity(DictSerializerMixin):
    _json: dict
    name: str
    type: int
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
    def __init__(self, **kwargs): ...

class ClientPresence(DictSerializerMixin):
    _json: dict
    since: Optional[int]
    activities: Optional[List[PresenceActivity]]
    status: str
    afk: bool
    def __init__(self, **kwargs): ...
