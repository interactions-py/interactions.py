from datetime import datetime
from typing import List, Optional

from .misc import DictSerializerMixin
from .user import User

class Member(DictSerializerMixin):
    __slots__ = (
        "_json",
        "user",
        "nick",
        "avatar",
        "roles",
        "joined_at",
        "premium_since",
        "deaf",
        "mute",
        "is_pending",
        "pending",
        "permissions",
    )

    _json: dict
    user: Optional[User]
    nick: Optional[str]
    avatar: Optional[str]
    roles: List[int]
    joined_at: datetime.timestamp
    premium_since: datetime
    deaf: bool
    mute: bool
    is_pending: Optional[bool]
    pending: Optional[bool]
    permissions: Optional[str]
    def __init__(self, **kwargs): ...
