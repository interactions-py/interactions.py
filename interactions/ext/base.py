from typing import Dict, List, Optional, Union

from setuptools import setup

from .error import UnknownService
from .version import Version


class Base:
    """
    A class representing the base structure of a 3rd party.

    :ivar Version version: The version of the library.
    :ivar str name: The name of the library.
    :ivar str description: The description of the library.
    :ivar Optional[str] long_description: The long description of the library.
    :ivar str link: The repository link or the library.
    :ivar Optional[List[str]] _packages: The packages of the library.
    :ivar Optional[List[str]] _requirements: The modules in the library required.
    :ivar Dict[str, object] __objects: The objects running under the service.
    """

    __slots__ = (
        "_packages",
        "_requirements",
        "_kwargs",
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
        packages: Optional[List[str]] = None,
        requirements: Optional[List[str]] = None,
        **kwargs: Optional[dict],
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
        :param packages?: The package(s) of the library. Defaults to ``None``.
        :type packages: Optional[List[str]]
        :param requirements?: The required modules needed for library function. Defaults to ``None``.
        :type requirements: Optional[List[str]]
        :param kwargs?: Any other keyword arguments. Defaults to ``None``.
        :type kwargs: Optional[dict]
        """
        self.version = version
        self.name = name
        self.link = link
        self.description = description
        self.long_description = long_description
        self._packages = packages
        self._requirements = requirements
        self._kwargs = kwargs
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

    def remove_service(self, name: str) -> Union[Exception, bool]:
        """
        Removes a service from the 3rd party in the event that it is no
        longer needed to be referred to for data.

        :param name: The name of the service to remove.
        :type name: str
        :return: If the service has been removed or not.
        :rtype: bool
        :raises UnknownService: An unknown service in the base.
        """
        _check: bool = self._check_service(name)

        if _check:
            del self.__objects[name]
        else:
            raise UnknownService
        return _check

    @property
    def services(self) -> Dict[str, object]:
        """
        Returns a view on all of the services currently stored under the 3rd party.

        :return: A dictionary of objects sorted by their name.
        :rtype: Dict[str, object]
        """
        return self.__objects


def build(base: Base) -> None:
    """Builds the base 3rd party the same way as ``setup`` from ``setuptools``."""
    setup(
        name=base.name,
        version=str(base.version),
        description=base.description,
        long_description="" if base.long_description is None else base.long_description,
        author=base.version.author,
        author_email=base.version.author.email,
        url=base.link,
        packages=[] if base._packages is None else base._packages,
        install_requires=[] if base._requirements is None else base._requirements,
        **base._kwargs,
    )
