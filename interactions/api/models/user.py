from .misc import DictSerializerMixin, Snowflake


class User(DictSerializerMixin):
    """
    A class object representing a user.

    :ivar Snowflake id: The User ID
    :ivar str username: The Username associated (not necessarily unique across the platform)
    :ivar str discriminator: The User's 4-digit discord-tag (i.e.: XXXX)
    :ivar Optional[str] avatar?: The user's avatar hash, if any.
    :ivar Optional[bool] bot?: A status denoting if the user is a bot.
    :ivar Optional[bool] system?: A status denoting if the user is an Official Discord System user.
    :ivar Optional[bool] mfa_enabled?: A status denoting if the user has 2fa on their account.
    :ivar Optional[str] banner?: The user's banner hash, if any.
    :ivar Optional[int] accent_color?: The user's banner color as an integer represented of hex color codes
    :ivar Optional[str] locale?: The user's chosen language option
    :ivar Optional[bool] verified?: Whether the email associated with this account has been verified
    :ivar Optional[str] email?: The user's email, if any.
    :ivar Optional[int] flags?: The user's flags
    :ivar Optional[int] premium_type?: The type of Nitro subscription the user has
    :ivar Optional[int] public_flags?: The user's public flags
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
