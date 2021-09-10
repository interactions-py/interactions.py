from datetime import datetime
from typing import Optional

from orjson import dumps

from .member import Member


class VoiceState(object):
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

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self._json = dumps(self.__dict__)


class VoiceRegion(object):
    _json: dict
    id: str
    name: str
    vip: bool
    optimal: bool
    deprecated: bool
    custom: bool

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self._json = dumps(self.__dict__)
