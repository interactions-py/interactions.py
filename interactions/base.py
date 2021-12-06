import logging
from typing import ClassVar

__version__ = "4.0.0"
__repo_url__ = "https://github.com/goverfl0w/discord-interactions"
__authors__ = {
    "current": [
        {"name": "James Walston<@goverfl0w>", "status": "Lead Developer"},
        {"name": "DeltaX<@DeltaXW>", "status": "Co-developer"},
    ],
    "old": [
        {"name": "Daniel Allen<@LordOfPolls>"},
        {"name": "eunwoo1104<@eunwoo1104>"},
    ],
}


class Data:
    """An object representing constants for the library."""

    LOGGER: ClassVar[int] = logging.DEBUG
