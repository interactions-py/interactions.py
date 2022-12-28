import logging

__all__ = (
    "get_logger",
    "__version__",
    "__authors__",
)

__version__ = "4.4.0-beta.1"

__authors__ = {
    "current": [
        {"name": "DeltaX<@DeltaXWizard>", "status": "Project Maintainer"},
        {"name": "Astrea<@Astrea49>", "status": "Developer"},
        {"name": "Toricane<@Toricane>", "status": "Developer"},
        {"name": "Catalyst<@Catalyst4222>", "status": "Developer"},
        {"name": "Damego<@Damego>", "status": "Developer"},
    ],
    "old": [
        {"name": "EdVraz<@EdVraz>"},
        {"name": "James Walston<@jameswalston>"},
        {"name": "Daniel Allen<@LordOfPolls>"},
        {"name": "eunwoo1104<@eunwoo1104>"},
    ],
}


get_logger = logging.getLogger
