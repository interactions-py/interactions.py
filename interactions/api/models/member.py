from datetime import datetime
from typing import List, Optional

from orjson import dumps, loads

from .user import User


class Member(object):
    """
    A class object representing the member of a guild.

    .. note::
        Also known as the guild member class object. (or partial)

        The methodology, instead of regular d.py conventions
        is to do member.user to get the pure User object, instead of
        d.py's option of merging.

        ``pending`` and ``permissions`` only apply for members retroactively
        requiring to verify rules via. membership screening or lack permissions
        to speak.

    :ivar interactions.api.models.user.User user: The user of the guild.
    :ivar str nick: The nickname of the member.
    :ivar typing.List[int] roles: The list of roles of the member.
    :ivar datetime.datetime.timestamp joined_at: The timestamp the member joined the guild at.
    :ivar datetime.datetime premium_since: The timestamp the member has been a server booster since.
    :ivar bool deaf: Whether the member is deafened.
    :ivar bool mute: Whether the member is muted.
    :ivar typing.Optional[bool] pending: Whether the member is pending to pass membership screening.
    :ivar typing.Optional[str] permissions: Whether the member has permissions.
    """

    __slots__ = (
        "_json",
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

    _json: dict
    user: Optional[User]
    nick: Optional[str]
    roles: List[int]
    joined_at: datetime.timestamp
    premium_since: datetime
    deaf: bool
    mute: bool
    pending: Optional[bool]
    permissions: Optional[str]

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self._json = loads(dumps(self.__dict__))
