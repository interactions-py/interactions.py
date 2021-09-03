from datetime import datetime
from typing import List, Optional

from .user import User


class Member(object):
    """
    Also, the guild member obj (Or partial.)

    The methodology, instead of regular d.py conventions
    is to do member.user to get the pure User object, instead of
    d.py's option of merging.
    """

    __slots__ = (
        "user",
        "nick",
        "roles",
        "joined_at",
        "premium_since",
        "deaf",
        "mute",
        "pending",
        "permissions",
    )

    user: Optional[User]
    nick: Optional[str]
    roles: List[int]
    joined_at: datetime.timestamp
    premium_since: datetime
    deaf: bool
    mute: bool
    pending: Optional[bool]
    permissions: Optional[str]
