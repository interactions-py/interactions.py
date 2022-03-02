from typing import ClassVar, Optional

class Route:

    __api__: ClassVar[str]
    method: str
    path: str
    channel_id: Optional[str]
    guild_id: Optional[str]

    def __init__(self, method: str, path: str, **kwargs) -> None: ...
    def get_bucket(self, shared_bucket: Optional[str] = None) -> str: ...
    @property
    def endpoint(self) -> str: ...
