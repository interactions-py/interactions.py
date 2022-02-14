from .flags import UserFlags
from .misc import DictSerializerMixin, Snowflake


class User(DictSerializerMixin):
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
    :ivar Optional[int] accent_color?: The user's banner color as an integer represented of hex color codes
    :ivar Optional[str] locale?: The user's chosen language option
    :ivar Optional[bool] verified?: Whether the email associated with this account has been verified
    :ivar Optional[str] email?: The user's email, if any
    :ivar Optional[UserFlags] flags?: The user's flags
    :ivar Optional[int] premium_type?: The type of Nitro subscription the user has
    :ivar Optional[UserFlags] public_flags?: The user's public flags
    """

    __slots__ = (
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if self._json.get("id") else None

        self.public_flags = (
            UserFlags(int(self._json.get("public_flags")))
            if self._json.get("public_flags")
            else None
        )

        self.flags = UserFlags(int(self._json.get("flags"))) if self._json.get("flags") else None

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
