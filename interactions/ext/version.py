from enum import Enum
from hashlib import md5
from string import ascii_lowercase
from typing import List, Optional, Union

from .error import IncorrectAlphanumeric, TooManyAuthors


class VersionAlphanumericType(str, Enum):
    ALPHA = "alpha"
    BETA = "beta"
    RELEASE_CANDIDATE = "rc"
    LETTER = ascii_lowercase


class VersionAuthor:
    """
    A class representing the author involved in a version.

    :ivar MD5Hash _hash: The hashed representation of the class.
    :ivar bool _co_author: Whether this is a co-author or not.
    :ivar bool active: Whether the author is active or not.
    :ivar str email: The email of the author.
    :ivar str name: The name of the author.
    """

    __slots__ = ("_hash", "_co_author", "active", "email", "name")

    def __init__(
        self,
        name,
        *,
        shared: Optional[bool] = False,
        active: Optional[bool] = True,
        email: Optional[str] = None,
    ) -> None:
        """
        :param name: The name of the author.
        :type name: str
        :param shared?: The author's relationship as the main or co-author. Defaults to ``False``.
        :type shared: Optional[bool]
        :param active?: The author's state of activity. Defaults to ``True``.
        :type active: Optional[bool]
        :param email?: The author's email address or point of contact. Defaults to ``None``.
        :type email: Optional[str]
        """
        self.name = name
        self._co_author = shared
        self.active = active
        self.email = email
        self._hash = md5(self.__str__())

    def __hash__(self):
        return self._hash

    def __str__(self) -> str:
        return f'{self.name}{f" <{self.email}>" if self.email else ""}'

    @property
    def is_co_author(self) -> bool:
        """Returns whether the author is a co-author or not."""
        return self._co_author

    @property
    def signature(self) -> str:
        return f"{'Co-authored by: ' if self._co_author else ''}{self.__str__()}"


class Version:
    """
    A class representing how a version is structured for a 3rd party library.

    .. note::
        This class respects the design and application of Semantic
        Versioning 2.0.0, (SemVer) a widely accepted standardisation
        of version control for modules and projects.

    :ivar int _major: The major version.
    :ivar int _minor: The minor version.
    :ivar int _patch: The patch version.
    :ivar List[VersionAuthor] _authors: The authors tied to the version release.
    :ivar str __version: The representation of the version.
    :ivar Optional[Dict[str, Union[int, VersionAlphanumericType]]] __alphanum: The alphanumeric typing of the version.
    """

    __slots__ = ("_major", "_minor", "_patch", "__version", "__alphanum")

    def __init__(self, **kwargs) -> None:
        """
        :param major?: The major version. If not specified, ``version`` will be read from.
        :type major: Optional[Union[str, int]]
        :param minor?: The minor version. If not specified, ``version`` will be read from.
        :type minor: Optional[Union[str, int]]
        :param patch?: The patch version. If not specified, ``version`` will be read from.
        :type patch: Optional[Union[str, int]]
        :param version?: The overall version. Must be used if ``major``, ``minor`` or ``patch`` are not.
        :type version: Optional[str]
        """
        self._major = int(kwargs.get("major") or kwargs.get("version", "0.0.0").split(".")[0])
        self._minor = int(kwargs.get("minor") or kwargs.get("version", "0.0.0").split(".")[1])
        self._patch = int(kwargs.get("patch") or kwargs.get("version", "0.0.0").split(".")[2])
        self._authors = kwargs.get("authors", []) or kwargs.get("author", [])
        self.__version = f"{self._major}.{self._minor}.{self._patch}"
        self.__alphanum = None

    def __repr__(self) -> str:
        return self.__version

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def major(self) -> int:
        """Returns the major version."""
        return self._major

    @property
    def minor(self) -> int:
        """Returns the minor version."""
        return self._minor

    @property
    def patch(self) -> int:
        """Returns the patch version."""
        return self._patch

    @property
    def author(self) -> Optional[Union[Exception, VersionAuthor]]:
        """
        Returns the author of the version.
        If multiple authors exist, it will choose the only one that is not a co-author.

        :return: The author of the version, if one exists.
        :rtype: Optional[VersionAuthor]
        :raises TooManyAuthors: Too many main authors were found.
        """
        _author: str = ""
        if len(self._authors) == 1:
            return self._authors
        elif len(self._authors) > 1:
            amount: int = 0
            for author in self._authors:
                if author.co_author:
                    amount += 1
                elif amount > 1:
                    raise TooManyAuthors
                else:
                    _author = author
                    continue
            return _author
        else:
            return None

    @property
    def authors(self) -> Optional[List[VersionAuthor]]:
        """
        Returns the list of authors under the version.

        :return: The authors of the version, if any exist.
        :rtype: Optional[List[VersionAuthor]]
        """
        if len(self._authors) > 1:
            return self._authors
        elif not len(self._authors):
            return None

    @property
    def is_alphanumeric(self) -> bool:
        """Returns whether the version is alphanumeric or not."""
        return bool(self.__alphanum)

    @classmethod
    def extend_version(cls, **kwargs) -> Union[Exception, str]:
        r"""
        Allows the version to be extended upon with an alphanumeric format.

        :param \**kwargs: Key-word arguments to be supplied as ``alpha``, ``beta`` or ``rc`` respectively.
        :type \**kwargs: Dict[VersionAlphanumericType, int]
        :return: The new version with the alphanumeric.
        :rtype: str
        :raises IncorrectAlphanumeric: The alphanumeric version was incorrectly formatted.
        """
        if "-" not in cls.__version:
            identifiers: tuple = (
                VersionAlphanumericType.ALPHA,
                VersionAlphanumericType.BETA,
                VersionAlphanumericType.RELEASE_CANDIDATE,
            )
            amount: int = 0
            for key, value in kwargs:
                if key in identifiers and len(value) == 1:
                    amount += 1
                    cls.__version = f"{cls.__version}-{key}.{value}"
                    cls.__alphanum = {"type": key, "identifier": int(value)}
                elif key in identifiers or amount > 1:
                    raise IncorrectAlphanumeric
                else:
                    continue

        return cls.__version
