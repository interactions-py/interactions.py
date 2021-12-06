from enum import IntEnum


class ApplicationCommandType(IntEnum):
    """
    An enumerable object representing the types of application commands.
    """

    CHAT_INPUT = 1
    USER = 2
    MESSAGE = 3
    AUTOCOMPLETE = 4


class InteractionType(IntEnum):
    """
    An enumerable object representing the types of interactions.
    """

    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5


class InteractionCallbackType(IntEnum):
    """
    An enumerable object representing the callback types of interaction responses.
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
    Enumerable object of literal integers holding equivocal values of a slash command's option(s).
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


class PermissionType(IntEnum):
    """
    Enumerable object of literal integers holding equivocal values of a slash command's permission(s).
    """

    ROLE = 1
    USER = 2


class ComponentType(IntEnum):
    """
    Enumerable object of literal integers holding equivocal values of a component(s) type.
    """

    ACTION_ROW = 1
    BUTTON = 2
    SELECT = 3
    INPUT_TEXT = 4


class ButtonStyle(IntEnum):
    """An enumerable object representing the styles of button components."""

    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5


class TextStyleType(IntEnum):
    """An enumerable object representing the styles of text inputs."""

    SHORT = 1
    PARAGRAPH = 2
