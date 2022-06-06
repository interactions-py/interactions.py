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
import colorsys
import random

from interactions.api.models.attrs_utils import MISSING, DictSerializerMixin, define, field
from interactions.base import get_logger

__all__ = (
    "DictSerializerMixin",
    "Snowflake",
    "Color",
    "ClientStatus",
    "Image",
    "File",
    "Overwrite",
    "MISSING",
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
    An object representing colors.
    """
    __slots__ = ("value",)

    def __init__(self, value):
        if not isinstance(value, int):
            raise TypeError(
                "Expected int parameter, received %s instead." % value.__class__.__name__
            )

        self.value = value

    def _get_byte(self, byte):
        return (self.value >> (8 * byte)) & 0xFF

    def __eq__(self, other):
        if not isinstance(other, Color):
            return NotImplementedError()
        return self.value == other.value

    def __str__(self):
        return "#{:0>6x}".format(self.value)

    def __repr__(self):
        return "<Colour value=%s>" % self.value

    def __hash__(self):
        return hash(self.value)

    @property
    def r(self):
        """:class:`int`: Returns the red component of the colour."""
        return self._get_byte(2)

    @property
    def g(self):
        """:class:`int`: Returns the green component of the colour."""
        return self._get_byte(1)

    @property
    def b(self):
        """:class:`int`: Returns the blue component of the colour."""
        return self._get_byte(0)

    def to_rgb(self):
        """Tuple[:class:`int`, :class:`int`, :class:`int`]: Returns an (r, g, b) tuple representing the colour."""
        return (self.r, self.g, self.b)

    @classmethod
    def from_rgb(cls, r, g, b):
        """Constructs a :class:`Colour` from an RGB tuple."""
        return cls((r << 16) + (g << 8) + b)

    @classmethod
    def from_hsv(cls, h, s, v):
        """Constructs a :class:`Colour` from an HSV tuple."""
        rgb = colorsys.hsv_to_rgb(h, s, v)
        return cls.from_rgb(*(int(x * 255) for x in rgb))

    @classmethod
    def default(cls):
        """A class method that returns a :class:`Colour` with a value of ``0``."""
        return cls(0)

    @classmethod
    def random(cls, *, seed=None):
        """A class method that returns a :class:`Colour` with a random hue.

        .. note::

            The random algorithm works by choosing a colour with a random hue but
            with maxed out saturation and value.
        Parameters
        ------------
        seed: Optional[Union[:class:`int`, :class:`str`, :class:`float`, :class:`bytes`, :class:`bytearray`]]
            The seed to initialize the RNG with. If ``None`` is passed the default RNG is used.

        """
        rand = random if seed is None else random.Random(seed)
        return cls.from_hsv(rand.random(), 1, 1)

    @classmethod
    def teal(cls):
        """A class method that returns a :class:`Colour` with a value of ``0x1abc9c``."""
        return cls(0x1ABC9C)

    @classmethod
    def dark_teal(cls):
        """A class method that returns a :class:`Colour` with a value of ``0x11806a``."""
        return cls(0x11806A)

    @classmethod
    def green(cls):
        """A class method that returns a :class:`Colour` with a value of ``0x2ecc71``."""
        return cls(0x2ECC71)

    @classmethod
    def dark_green(cls):
        """A class method that returns a :class:`Colour` with a value of ``0x1f8b4c``."""
        return cls(0x1F8B4C)

    @classmethod
    def blue(cls):
        """A class method that returns a :class:`Colour` with a value of ``0x3498db``."""
        return cls(0x3498DB)

    @classmethod
    def dark_blue(cls):
        """A class method that returns a :class:`Colour` with a value of ``0x206694``."""
        return cls(0x206694)

    @classmethod
    def purple(cls):
        """A class method that returns a :class:`Colour` with a value of ``0x9b59b6``."""
        return cls(0x9B59B6)

    @classmethod
    def dark_purple(cls):
        """A class method that returns a :class:`Colour` with a value of ``0x71368a``."""
        return cls(0x71368A)

    @classmethod
    def magenta(cls):
        """A class method that returns a :class:`Colour` with a value of ``0xe91e63``."""
        return cls(0xE91E63)

    @classmethod
    def dark_magenta(cls):
        """A class method that returns a :class:`Colour` with a value of ``0xad1457``."""
        return cls(0xAD1457)

    @classmethod
    def gold(cls):
        """A class method that returns a :class:`Colour` with a value of ``0xf1c40f``."""
        return cls(0xF1C40F)

    @classmethod
    def dark_gold(cls):
        """A class method that returns a :class:`Colour` with a value of ``0xc27c0e``."""
        return cls(0xC27C0E)

    @classmethod
    def orange(cls):
        """A class method that returns a :class:`Colour` with a value of ``0xe67e22``."""
        return cls(0xE67E22)

    @classmethod
    def dark_orange(cls):
        """A class method that returns a :class:`Colour` with a value of ``0xa84300``."""
        return cls(0xA84300)

    @classmethod
    def red(cls):
        """A class method that returns a :class:`Colour` with a value of ``0xed4245``."""
        return cls(0xED4245)

    @classmethod
    def dark_red(cls):
        """A class method that returns a :class:`Colour` with a value of ``0x992d22``."""
        return cls(0x992D22)

    @classmethod
    def lighter_grey(cls):
        """A class method that returns a :class:`Colour` with a value of ``0x95a5a6``."""
        return cls(0x95A5A6)

    @classmethod
    def dark_grey(cls):
        """A class method that returns a :class:`Colour` with a value of ``0x607d8b``."""
        return cls(0x607D8B)

    @classmethod
    def light_grey(cls):
        """A class method that returns a :class:`Colour` with a value of ``0x979c9f``."""
        return cls(0x979C9F)

    @classmethod
    def darker_grey(cls):
        """A class method that returns a :class:`Colour` with a value of ``0x546e7a``."""
        return cls(0x546E7A)

    @classmethod
    def blurple(cls):
        """A class method that returns a :class:`Colour` with a value of ``0x5865f2``."""
        return cls(0x5865F2)

    @classmethod
    def greyple(cls):
        """A class method that returns a :class:`Colour` with a value of ``0x99aab5``."""
        return cls(0x99AAB5)

    @classmethod
    def dark_theme(cls):
        """A class method that returns a :class:`Colour` with a value of ``0x36393F``.
        This will appear transparent on Discord's dark theme.
        """
        return cls(0x36393F)

    @classmethod
    def fuchsia(cls):
        """Returns a hexadecimal value of the fuchsia color."""
        return cls(0xEB459E)

    # I can't imagine any bot developers actually using these.
    # If they don't know white is ff and black is 00, something's seriously
    # wrong.

    @classmethod
    def white(cls):
        """Returns a hexadecimal value of the white color."""
        return cls(0xFFFFFF)

    @classmethod
    def black(cls):
        """Returns a hexadecimal value of the black color."""
        return cls(0x000000)


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
            raise TypeError(
                "File's first parameter 'filename' must be a string, not " +
                str(type(filename))
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
            raise ValueError("File type must be jpeg, png or gif!")

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
