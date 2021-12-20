from .misc import DictSerializerMixin, Snowflake


class RoleTags(DictSerializerMixin):
    """
    A class object representing the tags of a role.

    :ivar Optional[Snowflake] bot_id?: The id of the bot this role belongs to
    :ivar Optional[Snowflake] integration_id?: The id of the integration this role belongs to
    :ivar Optional[Any] premium_subscriber?: Whether if this is the guild's premium subscriber role
    """

    __slots__ = ("_json", "id", "bot_id", "integration_id", "premium_subscriber")

    # TODO: Figure out what actual type it returns, all it says is null.

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.bot_id = Snowflake(self.bot_id) if self._json.get("bot_id") else None
        self.integration_id = (
            Snowflake(self.integration_id) if self._json.get("integration_id") else None
        )


class Role(DictSerializerMixin):
    """
    A class object representing a role.

    :ivar Snowflake id: Role ID
    :ivar str name: Role name
    :ivar int color: Role color in integer representation
    :ivar bool hoist: A status denoting if this role is hoisted
    :ivar Optional[str] icon?: Role icon hash, if any.
    :ivar Optional[str] unicode_emoji?: Role unicode emoji
    :ivar int position: Role position
    :ivar str permissions: Role permissions as a bit set
    :ivar bool managed: A status denoting if this role is managed by an integration
    :ivar bool mentionable: A status denoting if this role is mentionable
    :ivar Optional[RoleTags] tags?: The tags this role has
    """

    __slots__ = (
        "_json",
        "id",
        "name",
        "color",
        "hoist",
        "icon",
        "unicode_emoji",
        "position",
        "managed",
        "mentionable",
        "tags",
        "permissions",
        "_client",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if self._json.get("id") else None
        self.tags = RoleTags(**self.tags) if self._json.get("tags") else None

    # TODO: edit, delete
