from .flags import UserFlags as UserFlags
from .misc import DictSerializerMixin as DictSerializerMixin, Snowflake as Snowflake, define as define, field as field, \
    ClientSerializerMixin
from typing import Optional


class User(ClientSerializerMixin):
    id: Snowflake
    username: str
    discriminator: str
    avatar: Optional[str]
    bot: Optional[bool]
    system: Optional[bool]
    mfa_enabled: Optional[bool]
    banner: Optional[str]
    accent_color: Optional[int]
    banner_color: Optional[str]
    locale: Optional[str]
    verified: Optional[bool]
    email: Optional[str]
    flags: Optional[UserFlags]
    premium_type: Optional[int]
    public_flags: Optional[UserFlags]
    bio: Optional[str]
    @property
    def mention(self) -> str: ...
    @property
    def avatar_url(self) -> str: ...
    @property
    def banner_url(self) -> Optional[str]: ...
