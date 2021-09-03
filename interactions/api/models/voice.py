from datetime import datetime
from typing import Optional

from .member import Member


class VoiceState(object):
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
