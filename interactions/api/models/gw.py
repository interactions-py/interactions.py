from .misc import DictSerializerMixin, Snowflake


class ChannelPins(DictSerializerMixin):
    __slots__ = ("_json", "guild_id", "channel_id", "last_pin_timestamp")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = Snowflake(self.guild_id) if hasattr(self, "guild_id") else None
        self.channel_id = Snowflake(self.channel_id) if hasattr(self, "channel_id") else None


class GuildBan(DictSerializerMixin):
    __slots__ = ("_json", "guild_id", "user")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = Snowflake(self.guild_id) if hasattr(self, "guild_id") else None


class GuildEmojis(DictSerializerMixin):
    __slots__ = ("_json", "guild_id", "emojis")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = Snowflake(self.guild_id) if hasattr(self, "guild_id") else None


class GuildIntegrations(DictSerializerMixin):
    __slots__ = ("_json", "guild_id")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = Snowflake(self.guild_id) if hasattr(self, "guild_id") else None


class GuildMember(DictSerializerMixin):
    __slots__ = (
        "_json",
        "guild_id",
        "roles",
        "user",
        "nick",
        "avatar",
        "joined_at",
        "premium_since",
        "deaf",
        "mute",
        "pending",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = Snowflake(self.guild_id) if hasattr(self, "guild_id") else None


class GuildMembers(DictSerializerMixin):
    __slots__ = (
        "_json",
        "guild_id",
        "members",
        "chunk_index",
        "chunk_count",
        "not_found",
        "presences",
        "nonce",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = Snowflake(self.guild_id) if hasattr(self, "guild_id") else None


class GuildRole(DictSerializerMixin):
    __slots__ = ("_json", "guild_id", "role", "role_id")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = Snowflake(self.guild_id) if hasattr(self, "guild_id") else None
        self.role_id = Snowflake(self.role_id) if hasattr(self, "role_id") else None


class GuildStickers(DictSerializerMixin):
    __slots__ = ("_json", "guild_id", "stickers")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = Snowflake(self.guild_id) if hasattr(self, "guild_id") else None


class Integration(DictSerializerMixin):
    ...
    # the difference between gw's implementation and guilds' is the Guild ID key.
    # TODO: Document guilds' implementation of integration

    __slots__ = (
        "_json",
        "id",
        "name",
        "type",
        "enabled",
        "syncing",
        "role_id",
        "enable_emoticons",
        "expire_behavior",
        "expire_grace_period",
        "user",
        "account",
        "synced_at",
        "subscriber_count",
        "revoked",
        "application",
        "guild_id",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if hasattr(self, "id") else None
        self.role_id = Snowflake(self.role_id) if hasattr(self, "role_id") else None
        self.guild_id = Snowflake(self.guild_id) if hasattr(self, "guild_id") else None


class Presence(DictSerializerMixin):
    __slots__ = ("_json", "user", "guild_id", "status", "activities", "client_status")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = Snowflake(self.guild_id) if hasattr(self, "guild_id") else None


class Reaction(DictSerializerMixin):
    __slots__ = ("_json", "user_id", "channel_id", "message_id", "guild_id", "member", "emoji")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_id = Snowflake(self.user_id) if hasattr(self, "user_id") else None
        self.channel_id = Snowflake(self.channel_id) if hasattr(self, "channel_id") else None
        self.message_id = Snowflake(self.message_id) if hasattr(self, "message_id") else None
        self.guild_id = Snowflake(self.guild_id) if hasattr(self, "guild_id") else None


class ReactionRemove(Reaction):
    __slots__ = ("_json", "user_id", "channel_id", "message_id", "guild_id", "emoji")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_id = Snowflake(self.user_id) if self.user_id else None
        self.channel_id = Snowflake(self.channel_id)
        self.message_id = Snowflake(self.message_id)
        self.guild_id = Snowflake(self.guild_id) if self.guild_id else None


class ThreadList(DictSerializerMixin):
    __slots__ = ("_json", "guild_id", "channel_ids", "threads", "members")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = Snowflake(self.guild_id) if hasattr(self, "guild_id") else None
        self.channel_ids = (
            [Snowflake(channel_id) for channel_id in self.channel_ids]
            if hasattr(self, "channel_ids")
            else None
        )


class ThreadMembers(DictSerializerMixin):
    __slots__ = ("_json", "id", "guild_id", "member_count", "added_members", "removed_member_ids")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if hasattr(self, "id") else None
        self.guild_id = Snowflake(self.guild_id) if hasattr(self, "guild_id") else None
        self.removed_member_ids = (
            [Snowflake(removed_member_id) for removed_member_id in self.removed_member_ids]
            if hasattr(self, "removed_member_ids")
            else None
        )
