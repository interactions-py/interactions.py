from typing import Dict, List, Optional

from setuptools import setup

from .error import UnknownServiceError
from .version import Version


class Base:
    """
    A class representing the base structure of a 3rd party.

    :ivar Version version: The version of the library.
    :ivar str name: The name of the library.
    :ivar str description: The description of the library.
    :ivar Optional[str] long_description: The long description of the library.
    :ivar str link: The repository link or the library.
    :ivar Optional[List[str]] _dependencies: The dependencies of the library needed.
    :ivar Optional[List[str]] _requirements: The modules in the library required.
    :ivar Dict[str, object] __objects: The objects running under the service.
    """

    __slots__ = (
        "_dependencies",
        "_requirements",
        "__objects",
        "version",
        "name",
        "description",
        "link",
    )

    def __init__(
        self,
        *,
        name: str,
        version: Version,
        link: str,
        description: str,
        long_description: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        requirements: Optional[List[str]] = None,
    ) -> None:
        """
        :param name: The name of the library.
        :type name: str
        :param version: The version of the library.
        :type version: Version
        :param link: The repository link of the library via. GitHub.
        :type link: str
        :param description: The description of the library, e.g. the purpose.
        :type description: str
        :param long_description?: The full description of the library, e.g. README. Defaults to ``None``.
        :type long_description: Optional[str]
        :param dependencies?: The dependencies/other modules needed for library function. Defaults to ``None``.
        :type dependencies: Optional[List[str]]
        :param requirements?: The required modules needed for library function. Defaults to ``None``.
        :type requirements: Optional[List[str]]
        """
        self.version = version
        self.name = name
        self.version = version
        self.link = link
        self.description = description
        self.long_description = long_description
        self._dependencies = dependencies
        self._requirements = requirements
        self.__objects = {}

    def _check_service(self, name: str) -> bool:
        """
        Checks whether the service already exists within the list or not.

        :param name: The name of the service to check.
        :type name: str
        :return: Whether the service exists or not.
        :rtype: bool
        """
        return bool(self.__objects.get(name))

    def add_service(self, obj: object, name: str) -> Dict[str, object]:
        """
        Adds a service to the 3rd party for ease of accessibility in calling.
        The code theory behind this is to simplify the way you handle and manage
        the calling of other objects, as well as accessing their information.

        :param obj: The object to add as a service.
        :type obj: object
        :param name: The name of the object to map under.
        :type name: str
        :return: The mapped relation between the object and name.
        :rtype: Dict[str, object]
        """
        model: Dict[str, object] = {name: obj}

        if self._check_service(model):
            self.__objects.update(model)
        return self.__objects.get(name)

    def remove_service(self, name: str) -> bool:
        """
        Removes a service from the 3rd party in the event that it is no
        longer needed to be referred to for data.

        :param name: The name of the service to remove.
        :type name: str
        :return: If the service has been removed or not.
        :rtype: bool
        """
        _check: bool = self._check_service(name)

        if _check:
            del self.__objects[name]
        else:
            raise UnknownServiceError
        return _check

    @property
    def services(self) -> Dict[str, object]:
        """
        Returns a view on all of the services currently stored under the 3rd party.

        :return: A dictionary of objects sorted by their name.
        :rtype: Dict[str, object]
        """
        return self.__objects

    def build(self) -> None:
        """Builds the base 3rd party the same way as ``setup`` from ``setuptools``."""
        setup(
            name=self.name,
            version=str(self.version),
            description=self.description,
            long_description="" if self.long_description is None else self.long_description,
            author=self.version.author,
            author_email=self.version.author.email,
            url=self.link,
            packages=[] if self._dependencies is None else self._dependencies,
            install_requires=[] if self._requirements is None else self._requirements,
        )
