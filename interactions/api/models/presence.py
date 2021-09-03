from datetime import datetime
from typing import List, Optional

from .message import Emoji
from .misc import ClientStatus
from .user import User


class _PresenceParty(object):
    id: Optional[str]
    size: Optional[List[int]]


class _PresenceAssets(object):
    large_image: Optional[str]
    large_text: Optional[str]
    small_image: Optional[str]
    small_text: Optional[str]


class _PresenceSecrets(object):
    join: Optional[str]
    spectate: Optional[str]
    match: Optional[str]


class _PresenceButtons(object):
    label: str
    url: str


class PresenceActivity(object):
    name: str
    type: int
    url: Optional[str]
    created_at: int
    timestamps: Optional[datetime]
    application_id: Optional[int]
    details: Optional[str]
    state: Optional[str]
    emoji: Optional[Emoji]
    party: Optional[_PresenceParty]
    assets: Optional[_PresenceAssets]
    secrets: Optional[_PresenceSecrets]
    instance: Optional[bool]
    flags: Optional[int]
    buttons: Optional[_PresenceButtons]


class PresenceUpdate(object):
    user: User
    guild_id: int
    status: str
    activities: List[PresenceActivity]
    client_status: ClientStatus
