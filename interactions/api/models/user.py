from typing import Optional, Union

from .attrs_utils import ClientSerializerMixin, define, field
from .flags import UserFlags
from .misc import Snowflake

__all__ = ("User",)


@define()
class User(ClientSerializerMixin):
    """
    A class object representing a user.

    :ivar Snowflake id: The User ID
    :ivar str username: The Username associated (not necessarily unique across the platform)
    :ivar str discriminator: The User's 4-digit discord-tag (i.e.: XXXX)
    :ivar Optional[str] avatar?: The user's avatar hash, if any
    :ivar Optional[bool] bot?: A status denoting if the user is a bot
    :ivar Optional[bool] system?: A status denoting if the user is an Official Discord System user
    :ivar Optional[bool] mfa_enabled?: A status denoting if the user has 2fa on their account
    :ivar Optional[str] banner?: The user's banner hash, if any
    :ivar Optional[str] banner_color?: The user's banner color as a hex, if any
    :ivar Optional[int] accent_color?: The user's banner color as an integer represented of hex color codes
    :ivar Optional[str] locale?: The user's chosen language option
    :ivar Optional[bool] verified?: Whether the email associated with this account has been verified
    :ivar Optional[str] email?: The user's email, if any
    :ivar Optional[UserFlags] flags?: The user's flags
    :ivar Optional[int] premium_type?: The type of Nitro subscription the user has
    :ivar Optional[UserFlags] public_flags?: The user's public flags
    """

    id: Snowflake = field(converter=Snowflake, repr=True)
    username: str = field(repr=True)
    discriminator: str = field(repr=True)
    avatar: Optional[str] = field(default=None)
    bot: Optional[bool] = field(default=None, repr=True)
    system: Optional[bool] = field(default=None)
    mfa_enabled: Optional[bool] = field(default=None)
    banner: Optional[str] = field(default=None)
    accent_color: Optional[int] = field(default=None)
    banner_color: Optional[str] = field(default=None)
    locale: Optional[str] = field(default=None)
    verified: Optional[bool] = field(default=None)
    email: Optional[str] = field(default=None)
    flags: Optional[UserFlags] = field(converter=UserFlags, default=None)
    premium_type: Optional[int] = field(default=None)
    public_flags: Optional[UserFlags] = field(converter=UserFlags, default=None)
    bio: Optional[str] = field(default=None)

    def __str__(self) -> str:
        return self.username

    def has_public_flag(self, flag: Union[UserFlags, int]) -> bool:
        if self.public_flags == 0 or self.public_flags is None:
            return False
        return bool(int(self.public_flags) & flag)

    @property
    def mention(self) -> str:
        """
        Returns a string that allows you to mention the given user.

        :return: The string of the mentioned user.
        :rtype: str
        """
        return f"<@{self.id}>"

    @property
    def avatar_url(self) -> str:
        """
        Returns the URL of the user's avatar

        :return: URL of the user's avatar.
        :rtype: str
        """
        url = "https://cdn.discordapp.com/"
        if self.avatar:
            url += f"avatars/{int(self.id)}/{self.avatar}"
            url += ".gif" if self.avatar.startswith("a_") else ".png"
        else:
            url += f"embed/avatars/{int(self.discriminator) % 5}.png"
        return url

    @property
    def banner_url(self) -> Optional[str]:
        """
        Returns the URL of the user's banner.

        :return: URL of the user's banner (None will be returned if no banner is set)
        :rtype: str
        """
        if not self.banner:
            return None

        url = f"https://cdn.discordapp.com/banners/{int(self.id)}/{self.banner}"
        url += ".gif" if self.banner.startswith("a_") else ".png"
        return url
