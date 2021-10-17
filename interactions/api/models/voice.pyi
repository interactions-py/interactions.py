from datetime import datetime
from typing import Optional

from .member import Member
from .misc import DictSerializerMixin

class VoiceState(DictSerializerMixin):
    _json: dict
    guild_id: Optional[int]
    channel_id: Optional[int]
    user_id: int
    member: Member
    session_id: str
    deaf: bool
    mute: bool
    self_deaf: bool
    self_mute: bool
    self_stream: Optional[bool]
    self_video: bool
    suppress: bool
    request_to_speak_timestamp: Optional[datetime]
    def __init__(self, **kwargs): ...

class VoiceRegion(DictSerializerMixin):
    _json: dict
    id: str
    name: str
    optimal: bool
    deprecated: bool
    custom: bool
    def __init__(self, **kwargs): ...

class Voice(VoiceState): ...
