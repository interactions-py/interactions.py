from datetime import datetime
from typing import Optional

from .member import Member
from .misc import DictSerializerMixin, Snowflake

class VoiceState(DictSerializerMixin):
    _json: dict
    guild_id: Optional[Snowflake]
    channel_id: Optional[Snowflake]
    user_id: int
    member: Member
    session_id: Snowflake
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
    id: Snowflake
    name: str
    optimal: bool
    deprecated: bool
    custom: bool
    def __init__(self, **kwargs): ...

class Voice(VoiceState):
    # All typehints are already pointed to VoiceState
    def __init__(self, **kwargs): ...
