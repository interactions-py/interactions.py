# Normal libraries
from typing import ClassVar

__version__: str = "4.0.0"


class Data:
    """An object representing constants for the library."""
    __slots__ = "LOGGER"
    LOGGER: ClassVar[str] = "interactions.log"


class Route:
    """An object representing different URL routing paths."""
    __slots__ = ("API", "GATEWAY")
    API: ClassVar[str] = "https://discord.com/api/v9"
    GATEWAY: ClassVar[str] = "wss://gateway.discord.gg/?v=9"