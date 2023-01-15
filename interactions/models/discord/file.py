from io import IOBase
from pathlib import Path
from typing import BinaryIO, Optional, Union

import attrs

__all__ = ("File", "open_file", "UPLOADABLE_TYPE")


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class File:
    """
    Representation of a file.

    Used for sending files to discord.

    """

    file: Union["IOBase", BinaryIO, "Path", str] = attrs.field(repr=True)
    """Location of file to send or the bytes."""
    file_name: Optional[str] = attrs.field(repr=True, default=None)
    """Set a filename that will be displayed when uploaded to discord. If you leave this empty, the file will be called `file` by default"""

    def open_file(self) -> BinaryIO:
        """
        Opens the file.

        Returns:
            A file-like BinaryIO object.

        """
        if isinstance(self.file, (IOBase, BinaryIO)):
            return self.file
        else:
            return open(str(self.file), "rb")


UPLOADABLE_TYPE = Union[File, IOBase, BinaryIO, Path, str]


def open_file(file: UPLOADABLE_TYPE) -> BinaryIO:
    """
    Opens the file.

    Args:
        file: The target file or path to file.

    Returns:
        A file-like BinaryIO object.

    """
    match file:
        case File():
            return file.open_file()
        case IOBase() | BinaryIO():
            return file
        case Path() | str():
            return open(str(file), "rb")
        case _:
            raise ValueError(f"{file} is not a valid file")
