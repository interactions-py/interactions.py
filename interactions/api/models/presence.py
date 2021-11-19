from .misc import DictSerializerMixin


class _PresenceParty(DictSerializerMixin):
    """
    :ivar typing.Optional[str] id: ID of the party.
    :ivar typing.Optional[typing.List[int]] size: An array denoting the party's current and max size
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class _PresenceAssets(DictSerializerMixin):
    """
    :ivar typing.Optional[str] large_image: ID for a large asset of the activity
    :ivar typing.Optional[str] large_text: Text associated with the large asset
    :ivar typing.Optional[str] small_image: ID for a small asset of the activity
    :ivar typing.Optional[str] small_text: Text associated with the small asset
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class _PresenceSecrets(DictSerializerMixin):
    """
    :ivar typing.Optional[str] join: Join secret
    :ivar typing.Optional[str] spectate: Spectate secret
    :ivar typing.Optional[str] match: Instanced match secret
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class _PresenceButtons(DictSerializerMixin):
    """
    :ivar str label: Text of the button
    :ivar str url: URL of the button
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class _PresenceTimestamp(DictSerializerMixin):
    """
    :ivar Optional[int] start: Unix time in ms when the activity started
    :ivar Optional[int] end: Unix time in ms when the activity ended
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class PresenceActivity(DictSerializerMixin):
    """
    An object that points to a RPC variant of a users'
    activity.

    :ivar name: The activity name
    :ivar type: The activity type
    :ivar typing.Optional[str] url: stream url (if type is 1)
    :ivar int created_at: Unix timestamp of when the activity was created to the User's session
    :ivar typing.Optional[_PresenceTimestamp] timestamps: Unix timestamps for start and/or end of the game
    :ivar typing.Optional[int] application_id: Application ID for the game
    :ivar typing.Optional[str] details: What the player is currently doing
    :ivar typing.Optional[str] state: Current party status
    :ivar typing.Optional[Emoji] emoji: The emoji used for the custom status
    :ivar typing.Optional[_PresenceParty] party: Info for the current players' party
    :ivar typing.Optional[_PresenceAssets] assets: Images for the presence and their associated hover texts
    :ivar typing.Optional[_PresenceSecrets] secrets: for RPC join/spectate
    :ivar typing.Optional[bool] instance: A status denoting if the activity is a game session
    :ivar typing.Optional[int] flags: activity flags
    :ivar typing.Optional[typing.List[_PresenceButtons]] buttons: Custom buttons shown in the RPC.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class PresenceUpdate(DictSerializerMixin):
    """
    Presence update object.

    :ivar User user: User object associated with the presence.
    :ivar int guild_id: ID of the guild.
    :ivar str status: Status type (idle, dnd, online, offline)
    :ivar List[PresenceActivity] activities: Users' current activities
    :ivar ClientStatus client_status: User's platform-based status
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
