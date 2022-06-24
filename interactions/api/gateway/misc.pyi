from typing import Optional, Union
from aiohttp import BasicAuth

class ProxyConfig:
    scheme: Optional[str]
    host: Optional[str]
    port: Optional[Union[str, int]]
    user: Optional[str]
    password: Optional[str]
    auth: Optional[BasicAuth]
    def __init__(
            self,
            *args,
            scheme: Optional[str] = "https",
            host: Optional[str] = None,
            port: Optional[Union[str, int]] = None,
            user: Optional[str] = None,
            password: Optional[str] = None,
    ) -> None:
        ...
    def __str__(self) -> str: ...
