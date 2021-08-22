import datetime
from typing import Optional, Union, List


class User(object):
    # TODO: Figure out ? placements.
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

    def __init__(self, **kwargs) -> None:
        for inst in self:
            for kwarg in kwargs:
                exec(f"self.{inst} = {kwarg}")

class Channel(object):
    """
    The big Channel model.

    The purpose of this model is to be used as a base class, and
    is never needed to be used directly.
    """

    id: int  # "Snowflake"
    type: int
    guild_id: Optional[int]
    position: Optional[int]
    # ?? permission overwrite
    name: str  # This apparently exists in DMs. Untested in v9, known in v6
    topic: Optional[str]
    nsfw: Optional[bool]
    last_message_id: Optional[int]
    bitrate: Optional[int]  # not really needed in our case
    user_limit: Optional[int]
    rate_limit_per_user: Optional[int]
    recipients = Optional[List[User]]
    icon: Optional[str]
    owner_id: Optional[int]
    application_id: Optional[int]
    parent_id: Optional[int]
    last_pin_timestamp: Optional[datetime.datetime.timestamp]
    rtc_region: Optional[str]
    video_quality_mode: Optional[int]
    message_count: Optional[int]
    member_count: Optional[int]
    # Thread attributes? not implemented yet
    default_auto_archive_duration: Optional[int]
    permissions: Optional[str]

    def __init__(self, **kwargs) -> None:
        for inst in self:
            for kwarg in kwargs:
                exec(f"self.{inst} = {kwarg}")


class Message(object):
    """
    The big Message model.

    The purpose of this model is to be used as a base class, and
    is never needed to be used directly.
    """
    id: int
    channel_id: int
    guild_id: Optional[int]
    # author, its a User object
    author = User
    # member, guild member obj
    content: str
    timestamp: datetime.datetime.timestamp
    edited_timestamp: Optional[datetime.datetime.timestamp]
    tts: bool
    mention_everyone: bool
    # mentions = array of Users, and maybe partial members
    # mention roles
    mention_roles = Optional[List[str]]
    # mention_channels
    # attachments
    # embeds
    # reactions
    nonce: Union[int, str]
    pinned: bool
    webhook_id: Optional[int]
    type: int
    # activity
    # application
    application_id = int
    # message_reference
    flags: int
    # reference: Message ???
    # interaction
    thread: Optional[Channel]

    # components
    # s sticker items
    # stickers

    def __init__(self, **kwargs) -> None:
        for inst in self:
            for kwarg in kwargs:
                exec(f"self.{inst} = {kwarg}")


class Emoji(object):
    id: Optional[int]
    name: Optional[str]
    roles = Optional[List[str]]
    user: Optional[User]
    require_colons: Optional[bool]
    managed: Optional[bool]
    animated: Optional[bool]
    available: Optional[bool]

    def __init__(self, **kwargs) -> None:
        for inst in self:
            for kwarg in kwargs:
                exec(f"self.{inst} = {kwarg}")


class RoleTags(object):
    bot_id: Optional[int]
    integration_id: Optional[int]
    premium_subscriber: Optional[int]

    def __init__(self, **kwargs) -> None:
        for inst in self:
            for kwarg in kwargs:
                exec(f"self.{inst} = {kwarg}")


class Role(object):
    id: int
    name: str
    color: int
    hoist: bool
    position: int
    permissions: str
    managed: bool
    mentionable: bool
    tags: Optional[RoleTags]

    def __init__(self, **kwargs) -> None:
        for inst in self:
            for kwarg in kwargs:
                exec(f"self.{inst} = {kwarg}")


