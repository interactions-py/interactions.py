import time
from enum import IntEnum
from typing import Any, List, Optional

from ...utils.attrs_utils import DictSerializerMixin, convert_list, define, field
from .emoji import Emoji
from .flags import StatusType
from .misc import Snowflake

__all__ = (
    "PresenceParty",
    "PresenceAssets",
    "PresenceSecrets",
    "PresenceTimestamp",
    "PresenceActivity",
    "PresenceActivityType",
    "ClientPresence",
)


@define()
class PresenceParty(DictSerializerMixin):
    """
    A class object representing the party data of a presence.

    :ivar Optional[Snowflake] id?: ID of the party.
    :ivar Optional[List[int]] size?: An array denoting the party's current and max size
    """

    id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    size: Optional[List[int]] = field(default=None)


@define()
class PresenceAssets(DictSerializerMixin):
    """
    A class object representing the assets of a presence.

    :ivar Optional[str] large_image?: ID for a large asset of the activity
    :ivar Optional[str] large_text?: Text associated with the large asset
    :ivar Optional[str] small_image?: ID for a small asset of the activity
    :ivar Optional[str] small_text?: Text associated with the small asset
    """

    large_image: Optional[str] = field(default=None)
    large_text: Optional[str] = field(default=None)
    small_image: Optional[str] = field(default=None)
    small_text: Optional[str] = field(default=None)


@define()
class PresenceSecrets(DictSerializerMixin):
    """
    A class object representing "secret" join information of a presence.

    :ivar Optional[str] join?: Join secret
    :ivar Optional[str] spectate?: Spectate secret
    :ivar Optional[str] match?: Instanced match secret
    """

    join: Optional[str] = field(default=None)
    spectate: Optional[str] = field(default=None)
    match: Optional[str] = field(default=None)


@define()
class PresenceTimestamp(DictSerializerMixin):
    """
    A class object representing the timestamp data of a presence.

    :ivar Optional[int] start?: Unix time in ms when the activity started
    :ivar Optional[int] end?: Unix time in ms when the activity ended
    """

    start: Optional[int] = field(default=None)
    end: Optional[int] = field(default=None)


class PresenceActivityType(IntEnum):
    """
    A class object representing all supported Discord activity types.
    """

    GAME = 0
    STREAMING = 1
    LISTENING = 2
    WATCHING = 3
    CUSTOM = 4
    COMPETING = 5


@define()
class PresenceActivity(DictSerializerMixin):
    """
    A class object representing the current activity data of a presence.

    .. note::
        When using this model to instantiate alongside the client, if you provide a type 1 ( or PresenceActivityType.STREAMING ),
        then the ``url`` attribute is necessary.

        The ``button`` attribute technically contains an object denoting Presence buttons. However, the gateway dispatches these
        as strings (of button labels) as bots don't read the button URLs.

    :ivar str name: The activity name
    :ivar Union[int, PresenceActivityType] type: The activity type
    :ivar Optional[str] url?: stream url (if type is 1)
    :ivar int created_at: Unix timestamp (in milliseconds) of when the activity was added to the user's session
    :ivar Optional[PresenceTimestamp] timestamps?: Unix timestamps for start and/or end of the game
    :ivar Optional[Snowflake] application_id?: Application ID for the game
    :ivar Optional[str] details?: What the player is currently doing
    :ivar Optional[str] state?: Current party status
    :ivar Optional[Emoji] emoji?: The emoji used for the custom status
    :ivar Optional[PresenceParty] party?: Info for the current players' party
    :ivar Optional[PresenceAssets] assets?: Images for the presence and their associated hover texts
    :ivar Optional[PresenceSecrets] secrets?: for RPC join/spectate
    :ivar Optional[bool] instance?: A status denoting if the activity is a game session
    :ivar Optional[int] flags?: activity flags
    :ivar Optional[List[str]] buttons?: Custom button labels shown in the status, if any.
    """

    name: str = field()
    type: PresenceActivityType = field(converter=PresenceActivityType)
    url: Optional[str] = field(default=None)
    created_at: int = field(default=0)  # for manually initializing
    timestamps: Optional[PresenceTimestamp] = field(converter=PresenceTimestamp, default=None)
    application_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    details: Optional[str] = field(default=None)
    state: Optional[str] = field(default=None)
    emoji: Optional[Emoji] = field(converter=Emoji, default=None)
    party: Optional[PresenceParty] = field(converter=PresenceParty, default=None)
    assets: Optional[PresenceAssets] = field(converter=PresenceAssets, default=None)
    secrets: Optional[PresenceSecrets] = field(converter=PresenceSecrets, default=None)
    instance: Optional[bool] = field(default=None)
    flags: Optional[int] = field(default=None)
    buttons: Optional[List[str]] = field(default=None)
    # TODO: document/investigate what these do.
    user: Optional[Any] = field(default=None)
    users: Optional[Any] = field(default=None)
    status: Optional[Any] = field(default=None)
    client_status: Optional[Any] = field(default=None)
    activities: Optional[Any] = field(default=None)
    sync_id: Optional[Any] = field(default=None)
    session_id: Optional[Any] = field(default=None)
    id: Optional[Any] = field(default=None)

    @property
    def gateway_json(self) -> dict:
        """
        This returns the JSON representing the ClientPresence sending via the Gateway.

        .. note::
            This is NOT used for standard presence activity reading by other users, i.e. User activity reading.
            You can use the `_json` attribute instead.
        """
        res = {"name": self.name, "type": self.type}
        if self.url:
            res["url"] = self.url
        return res


@define()
class ClientPresence(DictSerializerMixin):
    """
    An object that symbolizes the presence of the current client's session upon creation.

    :ivar Optional[int] since?: Unix time in milliseconds of when the client went idle. None if it is not idle.
    :ivar Optional[List[PresenceActivity]] activities: Array of activity objects.
    :ivar Union[str, StatusType] status: The client's new status.
    :ivar bool afk: Whether the client is afk or not.
    """

    since: Optional[int] = field(default=None)
    activities: Optional[List[PresenceActivity]] = field(
        converter=convert_list(PresenceActivity), default=None
    )
    status: StatusType = field(converter=StatusType)
    afk: bool = field(default=False)

    def __attrs_post_init__(self):
        if not self._json.get("since"):
            # If since is not provided by the developer...
            self.since = int(time.time() * 1000) if self.status == "idle" else 0
            self._json["since"] = self.since
        if not self._json.get("afk"):
            self.afk = self._json["afk"] = False
        if not self._json.get("activities"):
            self.activities = self._json["activities"] = []
