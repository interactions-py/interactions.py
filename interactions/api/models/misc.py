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
from typing import Optional, Union

from ...base import get_logger
from ..error import LibraryException
from .attrs_utils import MISSING, DictSerializerMixin, define, field

__all__ = (
    "Snowflake",
    "Color",
    "ClientStatus",
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
    :ivar str allow: Permission bit set.
    :ivar str deny: Permission bit set.
    """

    id: int = field()
    type: int = field()
    allow: str = field()
    deny: str = field()


@define()
class ClientStatus(DictSerializerMixin):
    """
    An object that symbolizes the status per client device per session.

    :ivar Optional[str] desktop?: User's status set for an active desktop application session
    :ivar Optional[str] mobile?: User's status set for an active mobile application session
    :ivar Optional[str] web?: User's status set for an active web application session
    """

    dektop: Optional[str] = field(default=None)
    mobile: Optional[str] = field(default=None)
    web: Optional[str] = field(default=None)


class Snowflake(object):
    """
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

    def __str__(self):
        # This is overridden for model comparison between IDs.
        return self._snowflake

    def __int__(self):
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

    def __hash__(self):
        return hash(self._snowflake)

    def __eq__(self, other):
        if isinstance(other, Snowflake):
            return str(self) == str(other)
        elif isinstance(other, int):
            return int(self) == other
        elif isinstance(other, str):
            return str(self) == other

        return NotImplemented

    def __repr__(self):
        return f"{self.__class__.__name__}({self._snowflake})"


class Color(object):
    """
    An object representing Discord branding colors.

    .. note::
        This object only intends to cover the branding colors
        and no others. The main reason behind this is due to
        the current accepted standard of using hex codes or other
        custom-defined colors.
    """

    @property
    def blurple(self) -> hex:
        """Returns a hexadecimal value of the blurple color."""
        return 0x5865F2

    @property
    def green(self) -> hex:
        """Returns a hexadecimal value of the green color."""
        return 0x57F287

    @property
    def yellow(self) -> hex:
        """Returns a hexadecimal value of the yellow color."""
        return 0xFEE75C

    @property
    def fuchsia(self) -> hex:
        """Returns a hexadecimal value of the fuchsia color."""
        return 0xEB459E

    @property
    def red(self) -> hex:
        """Returns a hexadecimal value of the red color."""
        return 0xED4245

    # I can't imagine any bot developers actually using these.
    # If they don't know white is ff and black is 00, something's seriously
    # wrong.

    @property
    def white(self) -> hex:
        """Returns a hexadecimal value of the white color."""
        return 0xFFFFFF

    @property
    def black(self) -> hex:
        """Returns a hexadecimal value of the black color."""
        return 0x000000


class File(object):
    """
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
                message=f"File's first parameter 'filename' must be a string, not + {str(type(filename))}",
                code=12,
            )

        self._fp = open(filename, "rb") if not fp or fp is MISSING else fp
        self._filename = basename(filename)

        if not description or description is MISSING:
            self._description = self._filename
        else:
            self._description = description

    def _json_payload(self, id):
        return {"id": id, "description": self._description, "filename": self._filename}


class Image(object):
    """
    This class object allows you to upload Images to the Discord API.

    If a fp is not given, this will try to open & send a local file at the location
    specified in the 'file' parameter.
    """

    def __init__(self, file: Union[str, FileIO], fp: Optional[IOBase] = MISSING):

        self._URI = "data:image/"

        if fp is MISSING or isinstance(file, FileIO):
            file: FileIO = file if isinstance(file, FileIO) else FileIO(file)

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
