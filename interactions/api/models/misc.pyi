from typing import Optional

# TODO: Reorganise these models based on which big obj uses little obj
# TODO: Potentially rename some model references to enums, if applicable
# TODO: Reorganise mixins to its own thing, currently placed here because circular import sucks.
# also, it should be serialiser* but idk, fl0w'd say something if I left it like that. /shrug

class DictSerializerMixin(object):
    __slots__ = "_json"

    _json: dict
    def __init__(self, **kwargs): ...

class Overwrite(DictSerializerMixin):
    __slots__ = ("_json", "id", "type", "allow", "deny")
    _json: dict
    id: int
    type: int
    allow: str
    deny: str
    def __init__(self, **kwargs): ...

class ClientStatus(DictSerializerMixin):
    __slots__ = ("_json", "desktop", "mobile", "web")
    _json: dict
    desktop: Optional[str]
    mobile: Optional[str]
    web: Optional[str]
    def __init__(self, **kwargs): ...
