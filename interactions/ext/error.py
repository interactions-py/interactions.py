from enum import Enum


class ErrorType(str, Enum):
    """
    An enumerable object representing the type of error responses raised.

    :ivar str INCORRECT_ALPHANUMERIC_VERSION: You cannot have more than one alphanumeric identifier, or identifier with a missing value.
    :ivar str MISSING_NUMERIC_VERSION: You cannot have a missing numerical value.
    :ivar str TOO_MANY_AUTHORS: A version can only have one main author. The rest of the authors must be co-authors.
    :ivar str UNKNOWN_SERVICE: The service specified does not exist.
    """

    INCORRECT_ALPHANUMERIC_VERSION = (
        "You cannot have more than one alphanumeric identifier, or identifier with a missing value."
    )
    MISSING_NUMERIC_VERSION = "You cannot have a missing numerical value."
    TOO_MANY_AUTHORS = (
        "A version can only have one main author. The rest of the authors must be co-authors."
    )
    UNKNOWN_SERVICE = "The service specified does not exist."


class IncorrectAlphanumeric(Exception):
    """An exception raised whenever a ``Version`` object has an incorrect alphanumeric formatting."""

    def __init__(self):
        super().__init__(ErrorType.INCORRECT_ALPHANUMERIC_VERSION)


class MissingNumeric(Exception):
    """An exception raised whenever a ``Version`` object has an incorrect numerical formatting."""

    def __init__(self):
        super().__init__(ErrorType.MISSING_NUMERIC_VERSION)


class TooManyAuthors(Exception):
    """An exception raised whenever a ``VersionAuthor`` object have too many "main" authors."""

    def __init__(self):
        super().__init__(ErrorType.TOO_MANY_AUTHORS)


class UnknownService(Exception):
    """An exception raised whenever a ``Base`` object cannot find a service."""

    def __init__(self):
        super().__init__(ErrorType.UNKNOWN_SERVICE)
