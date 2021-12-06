from datetime import datetime
from typing import Any, List, Optional

from .misc import DictSerializerMixin
from .role import Role
from .user import User

class Member(DictSerializerMixin):

    _json: dict
    user: Optional[User]
    nick: Optional[str]
    avatar: Optional[str]
    roles: List[Role]
    joined_at: datetime
    premium_since: datetime
    deaf: bool
    mute: bool
    is_pending: Optional[bool]
    pending: Optional[bool]
    permissions: Optional[str]
    communication_disabled_until: Optional[str]
    hoisted_role: Any  # TODO: Investigate what this is for when documented by Discord.
    def __init__(self, **kwargs): ...
