from .misc import DictSerializerMixin


class ChannelPins(DictSerializerMixin):
    __slots__ = ("_json", "guild_id", "channel_id", "last_pin_timestamp")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class GuildBan(DictSerializerMixin):
    __slots__ = ("_json", "guild_id", "user")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class GuildEmojis(DictSerializerMixin):
    __slots__ = ("_json", "guild_id", "emojis")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class GuildIntegrations(DictSerializerMixin):
    __slots__ = ("_json", "guild_id")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


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


class GuildRole(DictSerializerMixin):
    __slots__ = ("_json", "guild_id", "role", "role_id")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class GuildStickers(DictSerializerMixin):
    __slots__ = ("_json", "guild_id", "stickers")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Integration(DictSerializerMixin):
    ...
    # TODO: Make an actual integration data model in the guild file.


class Presence(DictSerializerMixin):
    __slots__ = ("_json", "user", "guild_id", "status", "activities", "client_status")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Reaction(DictSerializerMixin):
    __slots__ = ("_json", "user_id", "channel_id", "message_id", "guild_id", "member", "emoji")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ReactionRemove(Reaction):
    ...
    # TODO: look more into this. weird aliasing from the GW?


class ThreadList(DictSerializerMixin):
    __slots__ = ("_json", "guild_id", "channel_ids", "threads", "members")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ThreadMembers(DictSerializerMixin):
    __slots__ = ("_json", "id", "guild_id", "member_count", "added_members", "removed_member_ids")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
