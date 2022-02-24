from typing import Dict, List, Optional, Union

from .version import Version

class Base:
    _packages: Optional[List[str]]
    _requirements: Optional[List[str]]
    __objects: Dict[str, object]
    version: Version
    name: str
    description: str
    link: str
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
    ) -> None: ...
    def _check_service(self, name: str) -> bool: ...
    def add_service(self, obj: object, name: str) -> Dict[str, object]: ...
    def remove_service(self, name: str) -> Union[Exception, bool]: ...
    @property
    def services(self) -> Dict[str, object]: ...
def build(base: "Base") -> None: ...
