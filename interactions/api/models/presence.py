import time
from enum import IntEnum

from ..models import StatusType
from .misc import DictSerializerMixin, Snowflake


class PresenceParty(DictSerializerMixin):
    """
    A class object representing the party data of a presence.

    :ivar Optional[Snowflake] id?: ID of the party.
    :ivar Optional[List[int]] size?: An array denoting the party's current and max size
    """

    __slots__ = ("_json", "id", "size")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = Snowflake(self.id) if self._json.get("id") else None


class PresenceAssets(DictSerializerMixin):
    """
    A class object representing the assets of a presence.

    :ivar Optional[str] large_image?: ID for a large asset of the activity
    :ivar Optional[str] large_text?: Text associated with the large asset
    :ivar Optional[str] small_image?: ID for a small asset of the activity
    :ivar Optional[str] small_text?: Text associated with the small asset
    """

    __slots__ = ("_json", "large_image", "large_text", "small_image", "small_text")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class PresenceSecrets(DictSerializerMixin):
    """
    A class object representing "secret" join information of a presence.

    :ivar Optional[str] join?: Join secret
    :ivar Optional[str] spectate?: Spectate secret
    :ivar Optional[str] match?: Instanced match secret
    """

    __slots__ = ("_json", "join", "spectate", "match")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class PresenceButtons(DictSerializerMixin):
    """
    A class object representing the buttons of a presence.

    :ivar str label: Text of the button
    :ivar str url: URL of the button
    """

    __slots__ = ("_json", "label", "url")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class PresenceTimestamp(DictSerializerMixin):
    """
    A class object representing the timestamp data of a presence.

    :ivar Optional[int] start?: Unix time in ms when the activity started
    :ivar Optional[int] end?: Unix time in ms when the activity ended
    """

    __slots__ = ("_json", "start", "end")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


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


class PresenceActivity(DictSerializerMixin):
    """
    A class object representing the current activity data of a presence.

    .. note::
        When using this model to instantiate alongside the client, if you provide a type 1 ( or PresenceActivityType.STREAMING ), then
        the ``url`` attribute is necessary.

    :ivar str name: The activity name
    :ivar Union[int, PresenceActivityType] type: The activity type
    :ivar Optional[str] url?: stream url (if type is 1)
    :ivar Snowflake created_at: Unix timestamp of when the activity was created to the User's session
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
    :ivar Optional[List[PresenceButtons]] buttons?: Custom buttons shown in the RPC.
    """

    __slots__ = (
        "_json",
        "name",
        "type",
        "url",
        "created_at",
        "timestamps",
        "application_id",
        "details",
        "state",
        "emoji",
        "party",
        "assets",
        "secrets",
        "instance",
        "flags",
        "buttons",
        # TODO: document/investigate what these do.
        "user",
        "users",
        "status",
        "client_status",
        "activities",
        "sync_id",
        "session_id",
        "id",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._json["type"] = (
            self.type.value if isinstance(self.type, PresenceActivityType) else self.type
        )
        self.application_id = (
            Snowflake(self.application_id) if self._json.get("application_id") else None
        )
        self.created_at = (
            Snowflake((self._json.get("created_at") - 1420070400000) << 22)
            if self._json.get("created_at")
            else None
        )
        self.timestamps = (
            PresenceTimestamp(**self.timestamps) if self._json.get("timestamps") else None
        )
        self.party = PresenceParty(**self.party) if self._json.get("party") else None
        self.assets = PresenceAssets(**self.assets) if self._json.get("assets") else None
        self.secrets = PresenceSecrets(**self.secrets) if self._json.get("secrets") else None

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


class ClientPresence(DictSerializerMixin):
    """
    An object that symbolizes the presence of the current client's session upon creation.

    :ivar Optional[int] since?: Unix time in milliseconds of when the client went idle. None if it is not idle.
    :ivar Optional[List[PresenceActivity]] activities: Array of activity objects.
    :ivar Union[str, StatusType] status: The client's new status.
    :ivar bool afk: Whether the client is afk or not.
    """

    __slots__ = ("_json", "since", "activities", "status", "afk")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._json["status"] = (
            self.status.value if isinstance(self.status, StatusType) else self.status
        )
        self.activities = (
            [
                PresenceActivity(
                    **(activity if isinstance(activity, dict) else activity.gateway_json)
                )
                for activity in self._json.get("activities")
            ]
            if self._json.get("activities")
            else None
        )
        if self.activities:
            self._json["activities"] = [activity._json for activity in self.activities]
        if self.status == "idle" and not self._json.get("since"):
            # If since is not provided by the developer...
            self.since = int(time.time() * 1000)
            self._json["since"] = self.since
        if not self._json.get("afk"):
            self._json["afk"] = False
