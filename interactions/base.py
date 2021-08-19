# Normal libraries
from enum import Enum

class Data(Enum):
    """Enumerable object representing constants for the library."""
    VERSION = "4.0.0"
    LOGGER = "interactions.log"

class Route(Enum):
    """Enumerable object representing different route paths."""
    API = "https://discord.com/api/v9"
    GATEWAY = "wss://gateway.discord.gg/?v=9"