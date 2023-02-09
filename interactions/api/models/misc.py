# TODO: This is post-v4.
#   Reorganise these models based on which big obj uses little obj
#   Potentially rename some model references to enums, if applicable
#   Reorganise mixins to its own thing, currently placed here because circular import sucks.
# also, it should be serialiser* but idk, fl0w'd say something if I left it like that. /shrug
# pycharm says serializer for me /shrug

import datetime
from base64 import b64encode
from io import FileIO, IOBase
from logging import Logger
from math import floor
from os.path import basename
from typing import List, Optional, Union

from ...base import get_logger
from ...client.enums import IntEnum, StrEnum
from ...utils.attrs_utils import DictSerializerMixin, convert_int, convert_list, define, field
from ...utils.missing import MISSING
from ..error import LibraryException
from .flags import Permissions

__all__ = (
    "AutoModKeywordPresetTypes",
    "AutoModTriggerType",
    "AutoModMetaData",
    "AutoModActionTypes",
    "AutoModAction",
    "AutoModTriggerMetadata",
    "AllowedMentionType",
    "AllowedMentions",
    "Snowflake",
    "Color",
    "ClientStatus",
    "IDMixin",
    "Image",
    "File",
    "Overwrite",
)

log: Logger = get_logger("mixin")


@define()
class Overwrite(DictSerializerMixin):
    """
    This is used for the PermissionOverride object.

    :ivar str id: Role or User ID
    :ivar int type: Type that corresponds ot the ID; 0 for role and 1 for member.
    :ivar Permissions allow: Permission bit set.
    :ivar Permissions deny: Permission bit set.
    """

    id: int = field()
    type: int = field()
    allow: Permissions = field(converter=convert_int(Permissions))
    deny: Permissions = field(converter=convert_int(Permissions))


@define()
class ClientStatus(DictSerializerMixin):
    """
    An object that symbolizes the status per client device per session.

    :ivar Optional[str] desktop: User's status set for an active desktop application session
    :ivar Optional[str] mobile: User's status set for an active mobile application session
    :ivar Optional[str] web: User's status set for an active web application session
    """

    desktop: Optional[str] = field(default=None)
    mobile: Optional[str] = field(default=None)
    web: Optional[str] = field(default=None)


class Snowflake:
    """
    .. versionadded:: 4.0.0

    .. important::
        By default every ID in this library is of this class. This makes some information of them easier accessible.
        If you need the ID as :class:`int` or :class:`str` object, for example to store it in a database,
        just call ``str(id)`` or ``int(id)``.

    .. versionchanged:: 4.2.0
        Added ``__eq__``. You no longer have to convert this object to compare it to a string or integer

    The Snowflake object.

    This snowflake object will have features closely related to the
    API schema. In turn, compared to regular d.py's treated snowflakes,
    these will be treated as strings.


    (Basically, snowflakes will be treated as if they were from d.py 0.16.12)

    .. note::
        You can still provide integers to them, to ensure ease of use of transition and/or
        if discord API for some odd reason will switch to integer.
    """

    __slots__ = "_snowflake"

    # Slotting properties are pointless, they are not in-memory
    # and are instead computed in-model.

    def __init__(self, snowflake: Union[int, str, "Snowflake"]) -> None:
        self._snowflake = str(snowflake)

    def __str__(self) -> str:
        # This is overridden for model comparison between IDs.
        return self._snowflake

    def __int__(self) -> int:
        # Easier to use for HTTP calling instead of int(str(obj)).
        return int(self._snowflake)

    @property
    def increment(self) -> int:
        """
        This is the 'Increment' portion of the snowflake.
        This is incremented for every ID generated on that process.

        :return: An integer denoting the increment.
        """
        return int(self._snowflake) & 0xFFF

    @property
    def worker_id(self) -> int:
        """
        This is the Internal Worker ID of the snowflake.

        :return: An integer denoting the internal worker ID.
        """
        return (int(self._snowflake) & 0x3E0000) >> 17

    @property
    def process_id(self) -> int:
        """
        This is the Internal Process ID of the snowflake.

        :return: An integer denoting the internal process ID.
        """
        return (int(self._snowflake) & 0x1F000) >> 12

    @property
    def epoch(self) -> float:
        """
        This is the Timestamp field of the snowflake.

        :return: A float containing the seconds since Discord Epoch.
        """
        return floor(((int(self._snowflake) >> 22) + 1420070400000) / 1000)

    @property
    def timestamp(self) -> datetime.datetime:
        """
        The Datetime object variation of the Timestamp field of the snowflake.

        :return: The converted Datetime object from the Epoch. This respects UTC.
        """
        return datetime.datetime.utcfromtimestamp(self.epoch)

    # ---- Extra stuff that might be helpful.

    def __hash__(self) -> int:
        return hash(self._snowflake)

    def __eq__(self, other) -> bool:
        if isinstance(other, Snowflake):
            return str(self) == str(other)
        elif isinstance(other, int):
            return int(self) == other
        elif isinstance(other, str):
            return str(self) == other

        return NotImplemented

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._snowflake})"


class IDMixin:
    """
    .. versionadded:: 4.3.0

    A mixin to implement equality and hashing for models that have an id.
    """

    id: Snowflake

    def __eq__(self, other) -> bool:
        return (
            self.id is not None
            and isinstance(
                other, IDMixin
            )  # different classes can't share ids, covers cases like Member/User
            and self.id == other.id
        )

    def __hash__(self) -> int:
        return hash(self.id)


@define()
class AutoModMetaData(DictSerializerMixin):
    """
    .. versionadded:: 4.3.0

    A class object used to represent the AutoMod Action Metadata.

    .. note::
        This is not meant to be instantiated outside the Gateway.

    .. note::
        The maximum duration for duration_seconds is 2419200 seconds, aka 4 weeks.

    :ivar Optional[Snowflake] channel_id: Channel to which user content should be logged, if set.
    :ivar Optional[int] duration_seconds: Timeout duration in seconds, if timed out.
    """

    channel_id: Optional[Snowflake] = field(converter=Snowflake, default=None)
    duration_seconds: Optional[int] = field(default=None)


class AutoModTriggerType(IntEnum):
    """
    .. versionadded:: 4.3.0

    An enumeration for the different AutoMod trigger types.
    """

    KEYWORD = 1
    HARMFUL_LINK = 2
    SPAM = 3
    KEYWORD_PRESET = 4
    MENTION_SPAM = 5


class AutoModKeywordPresetTypes(IntEnum):
    """
    .. versionadded:: 4.3.0

    An enumeration for the different AutoMod keyword preset types.
    """

    PROFANITY = 1
    SEXUAL_CONTENT = 2
    SLURS = 3


class AutoModActionTypes(IntEnum):
    """
    .. versionadded:: 4.3.0

    An enumeration for the different AutoMod action types.
    """

    BLOCK_MESSAGE = 1
    SEND_ALERT_MESSAGE = 2
    TIMEOUT = 3


@define()
class AutoModAction(DictSerializerMixin):
    """
    .. versionadded:: 4.3.0

    A class object used for the ``AUTO_MODERATION_ACTION_EXECUTION`` event.

    .. note::
        This is not to be confused with the GW event ``AUTO_MODERATION_ACTION_EXECUTION``.
        This object is not the same as that dispatched object. Moreover, that dispatched object name will be
        ``AutoModerationAction``

    .. note::
        The metadata can be omitted depending on the action type.

    :ivar AutoModActionTypes type: Action type.
    :ivar AutoModMetaData metadata: Additional metadata needed during execution for this specific action type.
    """

    type: AutoModActionTypes = field(converter=AutoModActionTypes)
    metadata: Optional[AutoModMetaData] = field(converter=AutoModMetaData, default=None)


@define()
class AutoModTriggerMetadata(DictSerializerMixin):
    """
    .. versionadded:: 4.3.0

    A class object used to represent the trigger metadata from the AutoMod rule object.

    :ivar Optional[List[str]] keyword_filter: Words to match against content.
    :ivar Optional[List[str]] regex_patterns: Regular expression patterns to match against content.
    :ivar Optional[List[AutoModKeywordPresetTypes]] presets: The internally pre-defined wordsets which will be searched for in content.
    :ivar Optional[List[str]] allow_list: Substrings which will be exempt from triggering the preset trigger type.
    :ivar Optional[int] mention_total_limit: Total number of unique role and user mentions allowed per message (Maximum of 50)
    """

    keyword_filter: Optional[List[str]] = field(default=None)
    regex_patterns: Optional[List[str]] = field(default=None)
    presets: Optional[List[AutoModKeywordPresetTypes]] = field(
        converter=convert_list(AutoModKeywordPresetTypes), default=None
    )
    allow_list: Optional[List[str]] = field(default=None)
    mention_total_limit: Optional[int] = field(default=None)


class Color(IntEnum):
    """
    .. versionadded:: 4.2.0

    .. versionchanged:: 4.4.0
        Color class is now an Enum

    An object representing Discord branding colors.

    .. note::
        This object only intends to cover the branding colors
        and no others. The main reason behind this is due to
        the current accepted standard of using hex codes or other
        custom-defined colors.
    """

    BLURPLE = 0x5865F2
    GREEN = 0x57F287
    YELLOW = 0xFEE75C
    FUCHSIA = 0xEB459E
    RED = 0xED4245
    WHITE = 0xFFFFFF
    BLACK = 0x000000


class File:
    """
    .. versionadded:: 4.2.0

    A File object to be sent as an attachment along with a message.

    If a fp is not given, this will try to open & send a local file at the location
    specified in the 'filename' parameter.

    .. note::
        If a description is not given the file's basename is used instead.
    """

    def __init__(
        self, filename: str, fp: Optional[IOBase] = MISSING, description: Optional[str] = MISSING
    ):
        if not isinstance(filename, str):
            raise LibraryException(
                message=f"File's first parameter 'filename' must be a string, not {str(type(filename))}",
                code=12,
            )

        self._fp = open(filename, "rb") if not fp or fp is MISSING else fp
        self._filename = basename(filename)

        if not description or description is MISSING:
            self._description = self._filename
        else:
            self._description = description

    def _json_payload(self, id: int) -> dict:
        return {"id": id, "description": self._description, "filename": self._filename}


class Image:
    """
    .. versionadded:: 4.2.0

    This class object allows you to upload Images to the Discord API.

    If a fp is not given, this will try to open & send a local file at the location
    specified in the 'file' parameter.
    """

    def __init__(self, file: Union[str, FileIO], fp: Optional[IOBase] = MISSING):
        self._URI = "data:image/"

        if fp is MISSING or isinstance(file, FileIO):
            file: FileIO = file if isinstance(file, FileIO) else FileIO(file)  # noqa

            self._name = file.name
            _file = file.read()

        else:
            self._name = file
            _file = fp

        if (
            not self._name.endswith(".jpeg")
            and not self._name.endswith(".png")
            and not self._name.endswith(".gif")
        ):
            raise LibraryException(message="File type must be jpeg, png or gif!", code=12)

        self._URI += f"{'jpeg' if self._name.endswith('jpeg') else self._name[-3:]};"
        self._URI += f"base64,{b64encode(_file).decode('utf-8')}"

    @property
    def data(self) -> str:
        return self._URI

    @property
    def filename(self) -> str:
        """
        Returns the name of the file.
        """
        return self._name.split("/")[-1].split(".")[0]


class AllowedMentionType(StrEnum):
    """
    .. versionadded:: 4.3.2

    An enumerable object representing the allowed mention types
    """

    EVERYONE = "everyone"
    USERS = "users"
    ROLES = "roles"


@define()
class AllowedMentions(DictSerializerMixin):
    """
    .. versionadded:: 4.3.2

    A class object representing the allowed mentions object

    :ivar Optional[List[AllowedMentionType]] parse: An array of allowed mention types to parse from the content.
    :ivar Optional[List[int]] users: An array of user ids to mention.
    :ivar Optional[List[int]] roles: An array of role ids to mention.
    :ivar Optional[bool] replied_user: For replies, whether to mention the author of the message being replied to.
    """

    parse: Optional[List[AllowedMentionType]] = field(
        converter=convert_list(AllowedMentionType), default=None
    )
    users: Optional[List[int]] = field(default=None)
    roles: Optional[List[int]] = field(default=None)
    replied_user: Optional[bool] = field(default=None)
