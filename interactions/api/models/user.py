from .misc import DictSerializerMixin


class User(DictSerializerMixin):
    """
    The User object.

    :ivar int id: The User ID
    :ivar str username: The Username associated (not necessarily unique across the platform)
    :ivar str discriminator: The User's 4-digit discord-tag (#XXXX)
    :ivar typing.Optional[str]: The user's avatar hash, if any.
    :ivar typing.Optional[bool] bot: A status denoting if the user is a bot.
    :ivar typing.Optional[bool] system: A status denoting if the user is an Official Discord System user.
    :ivar typing.Optional[bool] mfa_enabled: A status denoting if the user has 2fa on their account.
    :ivar typing.Optional[str] banner: The user's banner hash, if any.
    :ivar typing.Optional[int] accent_color: The user's banner color as an integer represented of hex color codes
    :ivar typing.Optional[str] locale: The user's chosen language option
    :ivar typing.Optional[bool] verified: Whether the email associated with this account has been verified
    :ivar typing.Optional[str] email: The user's email, if any.
    :ivar typing.Optional[int] flags: The user's flags
    :ivar typing.Optional[int] premium_type: The type of Nitro subscription the user has
    :ivar typing.Optional[int] public_flags: The user's public flags
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
