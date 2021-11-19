from .misc import DictSerializerMixin


class VoiceState(DictSerializerMixin):
    """
    An object that denotes a user's voice connection status.

    :ivar typing.Optional[int] guild_id: The guild ID associated with this voice state.
    :ivar typing.Optional[int] channel_id: The channel ID associated
    :ivar int user_id: The user id this voice state is for
    :ivar Member member: The guild member this voice state is for
    :ivar str session_id: This voice state's session ID
    :ivar bool deaf: Whether this user is server deafened
    :ivar bool mute: Whether this user is server muted
    :ivar bool self_deaf: Whether this user is locally deafened
    :ivar bool self_mute: Whether this user is locally muted
    :ivar typing.Optional[bool] self_stream: Whether the user's streaming using "Go Live"
    :ivar bool self_video: Whether this user's camera is on
    :ivar bool suppress: Whether this user is muted by the current user
    :ivar typing.Optional[datetime] request_to_speak_timestamp: The timestamp when the user has requested to speak
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class VoiceRegion(DictSerializerMixin):
    """
    The voice region object.

    :ivar str id: The region's unique ID
    :ivar str name: The region's name
    :ivar bool optimal: A status denoting whether a server in this region is close to the current user's client
    :ivar bool deprecated: A status denoting whether this region is deprecated (Don't switch to these, if able)
    :ivar bool custom: A status denoting whether this is a custom voice region (for events, etc)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Voice(VoiceState):
    """
    The voice object that inherits from voice state.

    ..note::
        Likewise, currently, all documentation is a duplicate of VoiceState.

    :ivar typing.Optional[int] guild_id: The guild ID associated with this voice state.
    :ivar typing.Optional[int] channel_id: The channel ID associated
    :ivar int user_id: The user id this voice state is for
    :ivar Member member: The guild member this voice state is for
    :ivar str session_id: This voice state's session ID
    :ivar bool deaf: Whether this user is server deafened
    :ivar bool mute: Whether this user is server muted
    :ivar bool self_deaf: Whether this user is locally deafened
    :ivar bool self_mute: Whether this user is locally muted
    :ivar typing.Optional[bool] self_stream: Whether the user's streaming using "Go Live"
    :ivar bool self_video: Whether this user's camera is on
    :ivar bool suppress: Whether this user is muted by the current user
    :ivar typing.Optional[datetime] request_to_speak_timestamp: The timestamp when the user has requested to speak
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
