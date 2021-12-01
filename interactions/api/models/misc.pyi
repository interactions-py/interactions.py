from typing import Optional

# TODO: Reorganise these models based on which big obj uses little obj
# TODO: Potentially rename some model references to enums, if applicable
# TODO: Reorganise mixins to its own thing, currently placed here because circular import sucks.
# also, it should be serialiser* but idk, fl0w'd say something if I left it like that. /shrug

class DictSerializerMixin(object):

    _json: dict
    def __init__(self, **kwargs): ...

class Overwrite(DictSerializerMixin):
    _json: dict
    id: int
    type: int
    allow: str
    deny: str
    def __init__(self, **kwargs): ...

class ClientStatus(DictSerializerMixin):

    _json: dict
    desktop: Optional[str]
    mobile: Optional[str]
    web: Optional[str]
    def __init__(self, **kwargs): ...

class Format(DictSerializerMixin):
    USER: str = "<@{id}>"
    USER_NICK: str = "<@!{id}>"
    CHANNEL: str = "<#{id}>"
    ROLE: str = "<@&{id}>"
    EMOJI: str = "<:{name}:{id}>"
    EMOJI_ANIMATED: str = "<a:{name}:{id}>"
    TIMESTAMP: str = "<t:{timestamp}>"
    TIMESTAMP_SHORT_T: str = "<t:{timestamp}:t>"
    TIMESTAMP_LONG_T: str = "<t:{timestamp}:T>"
    TIMESTAMP_SHORT_D: str = "<t:{timestamp}:d>"
    TIMESTAMP_LONG_D: str = "<t:{timestamp}:D>"
    TIMESTAMP_SHORT_DT: str = TIMESTAMP
    TIMESTAMP_LONG_DT: str = "<t:{timestamp}:F>"
    TIMESTAMP_RELATIVE: str = "<t:{timestamp}:R>"
    def stylize(self, format: str, **kwargs) -> str: ...
