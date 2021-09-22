from typing import Optional

from orjson import dumps, loads

# TODO: Reorganise these models based on which big obj uses little obj
# TODO: Figure out ? placements.
# TODO: Potentially rename some model references to enums, if applicable


class Overwrite(object):
    """This is used for the PermissionOverride obj"""

    __slots__ = ("_json", "id", "type", "allow", "deny")
    _json: dict
    id: int
    type: int
    allow: str
    deny: str

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self._json = loads(dumps(self.__dict__))


class ClientStatus(object):
    __slots__ = ("_json", "desktop", "mobile", "web")
    _json: dict
    desktop: Optional[str]
    mobile: Optional[str]
    web: Optional[str]

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self._json = loads(dumps(self.__dict__))
