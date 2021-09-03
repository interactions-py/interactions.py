from typing import Optional

# TODO: Reorganise these models based on which big obj uses little obj
# TODO: Figure out ? placements.
# TODO: Potentially rename some model references to enums, if applicable


class Overwrite(object):
    """This is used for the PermissionOverride obj"""

    __slots__ = ("id", "type", "allow", "deny")
    id: int
    type: int
    allow: str
    deny: str


class ClientStatus(object):
    __slots__ = ("desktop", "mobile", "web")

    desktop: Optional[str]
    mobile: Optional[str]
    web: Optional[str]
