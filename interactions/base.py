import logging
from typing import List, Optional, Union

from colorama import Fore, Style, init

__version__ = "4.0.1"
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
    """A class representing constants for the library.

    :ivar LOGGERS List[str]: A list of all loggers registered from this library
    """

    # LOG_LEVEL: ClassVar[int] = logging.WARNING
    LOGGERS: List[str] = []


def get_logger(
    logger: Optional[Union[logging.Logger, str]] = None,
    handler: Optional[logging.Handler] = logging.NullHandler(),
) -> logging.Logger:
    _logger = logging.getLogger(logger) if isinstance(logger, str) else logger
    _logger_name = logger if isinstance(logger, str) else logger.name
    if len(_logger.handlers) > 1:
        _logger.removeHandler(_logger.handlers[0])
    _handler = handler
    _handler.setFormatter(CustomFormatter)
    # _handler.setLevel(Data.LOG_LEVEL)  # this is sort of useless
    _logger.addHandler(handler)

    Data.LOGGERS.append(_logger_name)
    return _logger


class CustomFormatter(logging.Formatter):
    """A class that allows for customized logged outputs from the library."""

    format: str = "%(levelname)s:%(name)s:(ln.%(lineno)d):%(message)s"
    formats: dict = {
        logging.DEBUG: Fore.CYAN + format + Fore.RESET,
        logging.INFO: Fore.GREEN + format + Fore.RESET,
        logging.WARNING: Fore.YELLOW + format + Fore.RESET,
        logging.ERROR: Fore.RED + format + Fore.RESET,
        logging.CRITICAL: Style.BRIGHT + Fore.RED + format + Fore.RESET + Style.NORMAL,
    }

    def __init__(self):
        super().__init__()
        init(autoreset=True)

    def format(self, record):
        log_format = self.formats.get(record.levelno)
        formatter = logging.Formatter(log_format)
        return formatter.format(record)
