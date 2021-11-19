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

    __slots__ = (
        "_json",
        "guild_id",
        "channel_id",
        "user_id",
        "member",
        "session_id",
        "deaf",
        "mute",
        "self_deaf",
        "self_mute",
        "self_stream",
        "self_video",
        "suppress",
        "request_to_speak_timestamp",
    )
    def __init__(self, **kwargs): ...

class VoiceRegion(DictSerializerMixin):
    _json: dict
    id: str
    name: str
    optimal: bool
    deprecated: bool
    custom: bool

    __slots__ = ("_json", "id", "name", "optimal", "deprecated", "custom")
    def __init__(self, **kwargs): ...

class Voice(VoiceState):
    # All typehints are already pointed to VoiceState

    __slots__ = (
        "_json",
        "guild_id",
        "channel_id",
        "user_id",
        "member",
        "session_id",
        "deaf",
        "mute",
        "self_deaf",
        "self_mute",
        "self_stream",
        "self_video",
        "suppress",
        "request_to_speak_timestamp",
    )
    def __init__(self, **kwargs): ...
