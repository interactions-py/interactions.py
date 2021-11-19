from typing import List, Optional

from .message import Emoji
from .misc import ClientStatus, DictSerializerMixin
from .user import User

class _PresenceParty(DictSerializerMixin):
    _json: dict
    id: Optional[str]
    size: Optional[List[int]]

    __slots__ = ("_json", "id", "size")
    def __init__(self, **kwargs): ...

class _PresenceAssets(DictSerializerMixin):
    _json: dict
    large_image: Optional[str]
    large_text: Optional[str]
    small_image: Optional[str]
    small_text: Optional[str]

    __slots__ = ("_json", "large_image", "large_text", "small_image", "small_text")
    def __init__(self, **kwargs): ...

class _PresenceSecrets(DictSerializerMixin):
    _json: dict
    join: Optional[str]
    spectate: Optional[str]
    match: Optional[str]

    __slots__ = ("_json", "join", "spectate", "match")
    def __init__(self, **kwargs): ...

class _PresenceButtons(DictSerializerMixin):
    _json: dict
    label: str
    url: str

    __slots__ = ("_json", "label", "url")
    def __init__(self, **kwargs): ...

class _PresenceTimestamp(DictSerializerMixin):
    _json: dict
    start: Optional[int]
    end: Optional[int]

    __slots__ = ("_json", "start", "end")
    def __init__(self, **kwargs): ...

class PresenceActivity(DictSerializerMixin):
    _json: dict
    name: str
    type: int
    url: Optional[str]
    created_at: int
    timestamps: Optional[_PresenceTimestamp]
    application_id: Optional[int]
    details: Optional[str]
    state: Optional[str]
    emoji: Optional[Emoji]
    party: Optional[_PresenceParty]
    assets: Optional[_PresenceAssets]
    secrets: Optional[_PresenceSecrets]
    instance: Optional[bool]
    flags: Optional[int]
    buttons: Optional[List[_PresenceButtons]]

    __slots__ = (
        "_json",
        "name",
        "type",
        "url",
        "created_at",
        "timestamps",
        "application_id",
        "details",
        "state",
        "emoji",
        "party",
        "assets",
        "secrets",
        "instance",
        "flags",
        "buttons",
    )
    def __init__(self, **kwargs): ...

class PresenceUpdate(DictSerializerMixin):
    _json: dict
    user: User
    guild_id: int
    status: str
    activities: List[PresenceActivity]
    client_status: ClientStatus

    __slots__ = ("_json", "user", "guild_id", "status", "activities", "client_status")
    def __init__(self, **kwargs): ...
