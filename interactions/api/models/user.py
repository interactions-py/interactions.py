from typing import Any, Optional

from orjson import dumps, loads


class User(object):
    __slots__ = (
        "__dict__",
        "_json",
        "id",
        "username",
        "discriminator",
        "avatar",
        "bot",
        "system",
        "mfa_enabled",
        "banner",
        "accent_color",
        "locale",
        "verified",
        "email",
        "flags",
        "premium_type",
        "public_flags",
    )
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

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self._json = loads(dumps(self.__dict__))
