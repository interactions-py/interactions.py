from typing import Optional

from .misc import DictSerializerMixin, Snowflake
from .flags import UserFlags, AppFlags

class User(DictSerializerMixin):
    _json: dict
    id: Snowflake
    username: str
    discriminator: str
    avatar: Optional[str]
    bot: Optional[bool]
    system: Optional[bool]
    mfa_enabled: Optional[bool]
    banner: Optional[str]
    accent_color: Optional[int]
    locale: Optional[str]
    verified: Optional[bool]
    email: Optional[str]
    flags: Optional[UserFlags]
    premium_type: Optional[int]
    public_flags: Optional[UserFlags]
    def __init__(self, **kwargs): ...
    @property
    def mention(self) -> str: ...
    @property
    def avatar_url(self) -> str: ...
