"""
Constants used throughout interactions.py.

Attributes:
    __version__ str: The version of the library.
    __repo_url__ str: The URL of the repository.
    __py_version__ str: The python version in use.
    logger_name str: The name of interactions.py's default logger. Invalid if a custom logger is passed to `Client` to replace the default logger.
    logger logging.Logger: The logger used throughout interactions.py. If a custom logger is passed to `Client`, this obj is replaced with the new logger.
    kwarg_spam bool: Should ``unused kwargs`` be logged.

    ACTION_ROW_MAX_ITEMS int: The maximum number of items in an action row.
    SELECTS_MAX_OPTIONS int: The maximum number of options a select may have.
    SELECT_MAX_NAME_LENGTH int: The max length of a select's name.

    CONTEXT_MENU_NAME_LENGTH int: The max length of a context menu's name.
    SLASH_CMD_NAME_LENGTH int: The max length of a slash command's name.
    SLASH_CMD_MAX_DESC_LENGTH int: The maximum length of a slash command's description.
    SLASH_CMD_MAX_OPTIONS int: The maximum number of options a slash command may have.
    SLASH_OPTION_NAME_LENGTH int: The maximum length of a slash option's name.

    EMBED_MAX_NAME_LENGTH int: The maximum length for an embed title
    EMBED_MAX_DESC_LENGTH int: The maximum length for an embed description
    EMBED_MAX_FIELDS int: The maximum number of fields for an embed
    EMBED_TOTAL_MAX int: The total combined number of characters for an embed
    PREMIUM_GUILD_LIMITS dict: Limits granted per premium level of a guild

    GLOBAL_SCOPE _sentinel: A sentinel that represents a global scope for application commands.
    MENTION_PREFIX _sentinel: A sentinel representing the bot will be mentioned for a prefix
    MISSING _sentinel: A sentinel value that indicates something has not been set

    T TypeVar: A type variable used for generic typing.
    Absent Union[T, Missing]: A type hint for a value that may be MISSING.

"""
import inspect
import logging
import os
import sys
from collections import defaultdict
from importlib.metadata import version as _v, PackageNotFoundError
from typing import TypeVar, Union, Callable, Coroutine

__all__ = (
    "__version__",
    "__repo_url__",
    "__py_version__",
    "__api_version__",
    "get_logger",
    "logger_name",
    "kwarg_spam",
    "DISCORD_EPOCH",
    "ACTION_ROW_MAX_ITEMS",
    "SELECTS_MAX_OPTIONS",
    "SELECT_MAX_NAME_LENGTH",
    "CONTEXT_MENU_NAME_LENGTH",
    "SLASH_CMD_NAME_LENGTH",
    "SLASH_CMD_MAX_DESC_LENGTH",
    "SLASH_CMD_MAX_OPTIONS",
    "SLASH_OPTION_NAME_LENGTH",
    "EMBED_MAX_NAME_LENGTH",
    "EMBED_MAX_DESC_LENGTH",
    "EMBED_MAX_FIELDS",
    "EMBED_TOTAL_MAX",
    "EMBED_FIELD_VALUE_LENGTH",
    "Singleton",
    "Sentinel",
    "GlobalScope",
    "Missing",
    "MentionPrefix",
    "GLOBAL_SCOPE",
    "MISSING",
    "MENTION_PREFIX",
    "PREMIUM_GUILD_LIMITS",
    "Absent",
    "T",
    "T_co",
    "LIB_PATH",
    "RECOVERABLE_WEBSOCKET_CLOSE_CODES",
    "NON_RESUMABLE_WEBSOCKET_CLOSE_CODES",
)

_ver_info = sys.version_info

repo_names = ("interactions.py", "discord-py-interactions")
for repo_name in repo_names:
    try:
        __version__ = _v(repo_name)
        break
    except PackageNotFoundError:
        __version__ = "0.0.0"


__repo_url__ = "https://github.com/interactions-py/interactions.py"
__py_version__ = f"{_ver_info[0]}.{_ver_info[1]}"
__api_version__ = 10
logger_name = "interactions"
_logger = logging.getLogger(logger_name)


def get_logger() -> logging.Logger:
    global _logger
    return _logger


default_locale = "english_us"
kwarg_spam = False

DISCORD_EPOCH = 1420070400000

ACTION_ROW_MAX_ITEMS = 5
SELECTS_MAX_OPTIONS = 25
SELECT_MAX_NAME_LENGTH = 100

CONTEXT_MENU_NAME_LENGTH = 32
SLASH_CMD_NAME_LENGTH = 32
SLASH_CMD_MAX_DESC_LENGTH = 100
SLASH_CMD_MAX_OPTIONS = 25
SLASH_OPTION_NAME_LENGTH = 100

EMBED_MAX_NAME_LENGTH = 256
EMBED_MAX_DESC_LENGTH = 4096
EMBED_MAX_FIELDS = 25
EMBED_TOTAL_MAX = 6000
EMBED_FIELD_VALUE_LENGTH = 1024


class Singleton(type):
    _instances = {}

    def __call__(self, *args, **kwargs) -> "Singleton":
        if self not in self._instances:
            self._instances[self] = super(Singleton, self).__call__(*args, **kwargs)
        return self._instances[self]


class Sentinel(metaclass=Singleton):
    @staticmethod
    def _get_caller_module() -> str:
        stack = inspect.stack()

        caller = stack[2][0]
        return caller.f_globals.get("__name__")

    def __init__(self) -> None:
        self.__module__ = self._get_caller_module()
        self.name = type(self).__name__

    def __repr__(self) -> str:
        return self.name

    def __reduce__(self) -> str:
        return self.name

    def __copy__(self) -> "Sentinel":
        return self

    def __deepcopy__(self, _) -> "Sentinel":
        return self


class GlobalScope(Sentinel, int):
    def __getattr__(self, _) -> "GlobalScope":
        return 0  # type: ignore

    def __hash__(self) -> int:
        return 0

    def __bool__(self) -> bool:
        return False


class Missing(Sentinel):
    def __getattr__(self, *_) -> None:
        return None

    def __bool__(self) -> bool:
        return False


class MentionPrefix(Sentinel):
    ...


GLOBAL_SCOPE = GlobalScope()
MISSING = Missing()
MENTION_PREFIX = MentionPrefix()

PREMIUM_GUILD_LIMITS = defaultdict(
    lambda: {"emoji": 50, "stickers": 5, "bitrate": 96000, "filesize": 26214400},
    {
        1: {"emoji": 100, "stickers": 15, "bitrate": 128000, "filesize": 26214400},
        2: {"emoji": 150, "stickers": 30, "bitrate": 256000, "filesize": 52428800},
        3: {"emoji": 250, "stickers": 60, "bitrate": 384000, "filesize": 104857600},
    },
)


GUILD_WELCOME_MESSAGES = (
    "{0} joined the party.",
    "{0} is here.",
    "Welcome, {0}. We hope you brought pizza.",
    "A wild {0} appeared.",
    "{0} just landed.",
    "{0} just slid into the server.",
    "{0} just showed up!",
    "Welcome {0}. Say hi!",
    "{0} hopped into the server.",
    "Everyone welcome {0}!",
    "Glad you're here, {0}.",
    "Good to see you, {0}.",
    "Yay you made it, {0}!",
)

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
Absent = Union[T, Missing]
AsyncCallable = Callable[..., Coroutine]

LIB_PATH = os.sep.join(__file__.split(os.sep)[:-2])
"""The path to the library folder."""

RECOVERABLE_WEBSOCKET_CLOSE_CODES = (4000, 4001, 4002, 4003, 4005, 4007, 4008, 4009)
NON_RESUMABLE_WEBSOCKET_CLOSE_CODES = (1000, 4007)
