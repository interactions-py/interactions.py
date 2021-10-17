from typing import Any, Optional

from .misc import DictSerializerMixin

class User(DictSerializerMixin):
    __dict__: Any
    _json: dict
    id: int
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
    flags: int
    premium_type: int
    public_flags: int
    def __init__(self, **kwargs): ...
