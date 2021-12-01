from .misc import DictSerializerMixin


class Member(DictSerializerMixin):
    """
    A class object representing the member of a guild.

    .. note::
        Also known as the guild member class object. (or partial)

        The methodology, instead of regular d.py conventions
        is to do member.user to get the pure User object, instead of
        d.py's option of merging.

        ``pending`` and ``permissions`` only apply for members retroactively
        requiring to verify rules via. membership screening or lack permissions
        to speak.

    :ivar interactions.api.models.user.User user: The user of the guild.
    :ivar str nick: The nickname of the member.
    :ivar Optional[str] avatar: The hash containing the user's guild avatar, if applicable.
    :ivar List[int] roles: The list of roles of the member.
    :ivar datetime.timestamp joined_at: The timestamp the member joined the guild at.
    :ivar datetime.datetime premium_since: The timestamp the member has been a server booster since.
    :ivar bool deaf: Whether the member is deafened.
    :ivar bool mute: Whether the member is muted.
    :ivar Optional[bool] pending / is_pending: Whether the member is pending to pass membership screening.
    :ivar Optional[str] permissions: Whether the member has permissions.
    """

    __slots__ = (
        "_json",
        "user",
        "nick",
        "avatar",
        "roles",
        "joined_at",
        "premium_since",
        "deaf",
        "mute",
        "is_pending",
        "pending",
        "permissions",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
