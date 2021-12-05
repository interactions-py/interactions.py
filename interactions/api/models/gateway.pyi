from datetime import datetime
from typing import List, Optional

from .channel import Channel, ThreadMember
from .member import Member
from .message import Emoji, Sticker
from .misc import ClientStatus, DictSerializerMixin
from .presence import PresenceActivity
from .role import Role
from .user import User

class ChannelPins(DictSerializerMixin):
    _json: dict
    guild_id: Optional[str]
    channel_id: str
    last_pin_timestamp: Optional[datetime]
    def __init__(self, **kwargs): ...

class GuildBan(DictSerializerMixin):
    _json: dict
    guild_id: str
    user: User
    def __init__(self, **kwargs): ...

class GuildEmojis(DictSerializerMixin):
    _json: dict
    guild_id: str
    emojis: List[Emoji]
    def __init__(self, **kwargs): ...

class GuildIntegrations(DictSerializerMixin):
    _json: dict
    guild_id: str
    def __init__(self, **kwargs): ...

class GuildMember(DictSerializerMixin):
    _json: dict
    guild_id: str
    roles: Optional[List[str]]
    user: Optional[User]
    nick: Optional[str]
    avatar: Optional[str]
    joined_at: Optional[datetime]
    premium_since: Optional[datetime]
    deaf: Optional[bool]
    mute: Optional[bool]
    pending: Optional[bool]
    def __init__(self, **kwargs): ...

class GuildMembers(DictSerializerMixin):
    _json: dict
    guild_id: str
    members: List[Member]
    chunk_index: int
    chunk_count: int
    not_found: Optional[list]
    presences: Optional[list]  # TODO: build Presence data model(s)
    nonce: Optional[str]
    def __init__(self, **kwargs): ...

class GuildRole(DictSerializerMixin):
    _json: dict
    guild_id: str
    role: Role
    role_id: Optional[str]
    def __init__(self, **kwargs): ...

class GuildStickers(DictSerializerMixin):
    _json: dict
    guild_id: str
    stickers: List[Sticker]
    def __init__(self, **kwargs): ...

class Integration(DictSerializerMixin): ...

class Presence(DictSerializerMixin):
    _json: dict
    user: User
    guild_id: str
    status: str
    activities: List[PresenceActivity]
    client_status: ClientStatus

class Reaction(DictSerializerMixin):
    # There's no official data model for this, so this is psuedo for the most part here.
    _json: dict
    user_id: Optional[str]
    channel_id: str
    message_id: str
    guild_id: Optional[str]
    member: Optional[str]
    emoji: Optional[Emoji]
    def __init__(self, **kwargs): ...

class ReactionRemove(Reaction): ...  # TODO: look more into this. weird aliasing from the GW?

class ThreadList(DictSerializerMixin):
    _json: dict
    guild_id: str
    channel_ids: Optional[List[str]]
    threads: List[Channel]
    members: List[ThreadMember]
    def __init__(self, **kwargs): ...

class ThreadMembers(DictSerializerMixin):
    _json: dict
    id: str
    guild_id: str
    member_count: int
    added_members: Optional[List[ThreadMember]]
    removed_member_ids: Optional[List[str]]
    def __init__(self, **kwargs): ...
