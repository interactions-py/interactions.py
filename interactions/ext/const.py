from numbers import Number
from string import ascii_letters

from ...interactions.base import __version__ as __lib_version__

__version__ = f"{__lib_version__}:"


class Version:
    """A simplified class to return a formatted version."""

    def __new__(cls, *args) -> None:
        if isinstance([arg for arg in args], Number):
            if args[-1] not in ascii_letters:
                return [".".join(args) for arg in args][0]
            else:
                return [".".join(args[:-1]) for arg in args][0] + args[-1]
