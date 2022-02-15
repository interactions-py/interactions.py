from enum import Enum, IntEnum


class ApplicationCommandType(IntEnum):
    """
    An enumerable object representing the types of application commands.

    :ivar CHAT_INPUT: 1
    :ivar USER: 2
    :ivar MESSAGE: 3
    :ivar AUTOCOMPLETE: 4
    """

    CHAT_INPUT = 1
    USER = 2
    MESSAGE = 3
    AUTOCOMPLETE = 4


class InteractionType(IntEnum):
    """
    An enumerable object representing the types of interactions.

    :ivar PING: 1
    :ivar APPLICATION_COMMAND: 2
    :ivar MESSAGE_COMPONENT: 3
    :ivar APPLICATION_COMMAND_AUTOCOMPLETE: 4
    :ivar MODAL_SUBMIT: 5
    """

    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5


class InteractionCallbackType(IntEnum):
    """
    An enumerable object representing the callback types of interaction responses.

    :ivar PONG: 1
    :ivar CHANNEL_MESSAGE_WITH_SOURCE: 4
    :ivar DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE: 5
    :ivar DEFERRED_UPDATE_MESSAGE: 6
    :ivar UPDATE_MESSAGE: 7
    :ivar APPLICATION_COMMAND_AUTOCOMPLETE_RESULT: 8
    :ivar MODAL: 9
    """

    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
    DEFERRED_UPDATE_MESSAGE = 6
    UPDATE_MESSAGE = 7
    APPLICATION_COMMAND_AUTOCOMPLETE_RESULT = 8
    MODAL = 9


class OptionType(IntEnum):
    """
    An enumerable object representing the types of an application command option.

    :ivar SUB_COMMAND: 1
    :ivar SUB_COMMAND_GROUP: 2
    :ivar STRING: 3
    :ivar INTEGER: 4
    :ivar BOOLEAN: 5
    :ivar USER: 6
    :ivar CHANNEL: 7
    :ivar ROLE: 8
    :ivar MENTIONABLE: 9
    :ivar NUMBER: 10
    :ivar ATTACHMENT: 11
    """

    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
    MENTIONABLE = 9
    NUMBER = 10
    ATTACHMENT = 11


class PermissionType(IntEnum):
    """
    Enumerable object of literal integers holding equivocal values of a slash command's permission(s).

    :ivar ROLE: 1
    :ivar USER: 2
    :ivar CHANNEL: 3
    """

    ROLE = 1
    USER = 2
    CHANNEL = 3


class ComponentType(IntEnum):
    """
    An enumerable object representing the types of a component.

    :ivar ACTION_ROW: 1
    :ivar BUTTON: 2
    :ivar SELECT: 3
    :ivar INPUT_TEXT: 4
    """

    ACTION_ROW = 1
    BUTTON = 2
    SELECT = 3
    INPUT_TEXT = 4


class ButtonStyle(IntEnum):
    """
    An enumerable object representing the styles of button components.

    :ivar PRIMARY: 1
    :ivar SECONDARY: 2
    :ivar SUCCESS: 3
    :ivar DANGER: 4
    :ivar LINK: 5
    """

    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5


class TextStyleType(IntEnum):
    """
    An enumerable object representing the styles of text inputs.

    :ivar SHORT: 1
    :ivar PARAGRAPH: 2
    """

    SHORT = 1
    PARAGRAPH = 2


class Locale(str, Enum):
    """
    An enumerable object representing Discord locales.
    """

    ENGLISH_US = "en_US"
    ENGLISH_GB = "en_GB"
    BULGARIAN = "bg"
    CHINESE_CHINA = "zh-CN"
    CHINESE_TAIWAN = "zh-TW"
    CROATIAN = "hr"
    CZECH = "cs"
    DANISH = "da"
    DUTCH = "nl"
    FINNISH = "fi"
    FRENCH = "fr"
    GERMAN = "de"
    GREEK = "el"
    HINDI = "hi"
    HUNGARIAN = "hu"
    ITALIAN = "it"
    JAPANESE = "ja"
    KOREAN = "ko"
    LITHUANIAN = "lt"
    NORWEGIAN = "no"
    POLISH = "pl"
    PORTUGUESE_BRAZIL = "pt-BR"
    ROMANIAN = "ro"
    RUSSIAN = "ru"
    SPANISH_SPAIN = "es-ES"
    SWEDISH = "sv-SE"
    THAI = "th"
    TURKISH = "tr"
    UKRAINIAN = "uk"
    VIETNAMESE = "vi"
