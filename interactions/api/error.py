from enum import IntEnum
from string import Formatter
from typing import Any, Optional, Union


class ErrorFormatter(Formatter):
    """A customized error formatting script to return specific errors."""

    def get_value(self, key, args, kwargs) -> Any:
        if not isinstance(key, str):
            return Formatter.get_value(self, key=key, args=args, kwargs=kwargs)
        try:
            return kwargs[key]
        except KeyError:
            return key


class InteractionException(Exception):
    """
    An exception class for interactions.

    .. note::
        This is a WIP. This isn't meant to be used yet, this is a baseline,
        and for extensive testing/review before integration.
        Likewise, this will show the concepts before use, and will be refined when time goes on.

    :ivar interactions.api.error.ErrorFormatter _formatter: The built-in formatter.
    :ivar dict _lookup: A dictionary containing the values from the built-in Enum.

    """

    __slots__ = ("_type", "_lookup", "__type", "_formatter", "kwargs")

    def __init__(self, __type: Optional[Union[int, IntEnum]] = 0, **kwargs) -> None:
        """
        :param __type: Type of error. This is decided from an IntEnum, which gives readable error messages instead of
        typical error codes. Subclasses of this class works fine, and so does regular integers.
        :type __type: Optional[Union[int, IntEnum]]
        :param kwargs: Any additional keyword arguments.
        :type **kwargs: dict

        :: note::
            (given if 3 is "DUPLICATE_COMMAND" and with the right enum import, it will display 3 as the error code.)
            Example:

            >>> raise InteractionException(2, message="msg")
            Exception raised: "msg" (error 2)

            >>> raise InteractionException(Default_Error_Enum.DUPLICATE_COMMAND)  # noqa
            Exception raised: Duplicate command name. (error 3)
        """

        self._type = __type
        self.kwargs = kwargs
        self._formatter = ErrorFormatter()
        self._lookup = self.lookup()

        self.error()

    @staticmethod
    def lookup() -> dict:
        """
        From the default error enum integer declaration,
        generate a dictionary containing the phrases used for the errors.
        """
        return {
            0: "Unknown error",
            1: "Request to Discord API has failed.",
            2: "Some formats are incorrect. See Discord API DOCS for proper format.",
            3: "There is a duplicate command name.",
            4: "There is a duplicate component callback.",
            5: "There are duplicate `Interaction` instances.",  # rewrite to v4's interpretation
            6: "Command check has failed.",
            7: "Type passed was incorrect.",
            8: "Guild ID type passed was incorrect",
            9: "Incorrect data was passed to a slash command data object.",
            10: "The interaction was already responded to.",
            11: "Error creating your command.",
        }

    @property
    def type(self) -> Optional[Union[int, IntEnum]]:
        """
        Grabs the type attribute.
        Primarily useful to use it in conditions for integral v4 (potential) logic.
        """
        return self._type

    def error(self) -> None:
        """This calls the exception."""
        _err_val = ""
        _err_unidentifiable = False
        _empty_space = " "
        _overrided = "message" in self.kwargs

        if issubclass(type(self._type), IntEnum):
            _err_val = self.type.name
            _err_rep = self.type.value
        elif type(self.type) == int:
            _err_rep = self.type
        else:  # unidentifiable.
            _err_rep = 0
            _err_unidentifiable = True

        _err_msg = _default_err_msg = "Error code: {_err_rep}"

        if self.kwargs != {} and _overrided:
            _err_msg = self.kwargs["message"]

        self.kwargs["_err_rep"] = _err_rep

        if not _err_unidentifiable:
            lookup_str = self._lookup[_err_rep] if _err_rep in self._lookup.keys() else _err_val
            _lookup_str = (
                lookup_str
                if max(self._lookup.keys()) >= _err_rep >= min(self._lookup.keys())
                else ""
            )
        else:
            _lookup_str = lookup_str = ""

        custom_err_str = (
            self._formatter.format(_err_msg, **self.kwargs)
            if "_err_rep" in _err_msg
            else self._formatter.format(_err_msg + _empty_space + _default_err_msg, **self.kwargs)
        )

        # This is just for writing notes meant to be for the developer(testers):
        #
        # Error code 4 represents dupe callback. In v3, that's "Duplicate component callback detected: "
        #             f"message ID {message_id or '<any>'}, "
        #             f"custom_id `{custom_id or '<any>'}`, "
        #             f"component_type `{component_type or '<any>'}`"
        #
        # Error code 3 represents dupe command, i.e. "Duplicate command name detected: {name}"
        # Error code 1 represents Req. failure, i.e. "Request failed with resp: {self.status} | {self.msg}"
        #

        super().__init__(
            f"{f'{lookup_str} ' if _err_val != '' else f'{_lookup_str + _empty_space if max(self._lookup.keys()) >= _err_rep >= min(self._lookup.keys()) else lookup_str}'}{custom_err_str}"
        )


class GatewayException(InteractionException):
    """
    This is a derivation of InteractionException in that this is used to represent Gateway closing OP codes.

    :ivar ErrorFormatter _formatter: The built-in formatter.
    :ivar dict _lookup: A dictionary containing the values from the built-in Enum.
    """

    __slots__ = ("_type", "_lookup", "__type", "_formatter", "kwargs")

    def __init__(self, __type, **kwargs):
        super().__init__(__type, **kwargs)

    @staticmethod
    def lookup() -> dict:
        return {
            4000: "Unknown error. Try reconnecting?",
            4001: "Unknown opcode. Check your gateway opcode and/or payload.",
            4002: "Invalid payload.",
            4003: "Not authenticated",
            4004: "Improper token has been passed.",
            4005: "Already authenticated.",
            4007: "Invalid seq. Please reconnect and start a new session.",
            4008: "Rate limit exceeded. Slow down!",
            4009: "Timed out. Reconnect and try again.",
            4010: "Invalid shard.",
            4011: "Sharding required.",
            4012: "Invalid API version for the Gateway.",
            4013: "Invalid intent(s).",
            4014: "Some intent(s) requested are not allowed. Please double check.",
        }


class HTTPException(InteractionException):
    """
    This is a derivation of InteractionException in that this is used to represent HTTP Exceptions.

    :ivar ErrorFormatter _formatter: The built-in formatter.
    :ivar dict _lookup: A dictionary containing the values from the built-in Enum.
    """

    __slots__ = ("_type", "_lookup", "__type", "_formatter", "kwargs")

    def __init__(self, __type, **kwargs):
        super().__init__(__type, **kwargs)

    @staticmethod
    def lookup() -> dict:
        return {
            400: "Bad Request. The request was improperly formatted, or the server couldn't understand it.",
            401: "Not authorized. Double check your token to see if it's valid.",
            403: "You do not have enough permissions to execute this.",
            404: "Resource does not exist.",
            405: "HTTP method not valid.",  # ?
            429: "You are being rate limited. Please slow down on your requests.",  # Definitely can be overclassed.
            502: "Gateway unavailable. Try again later.",
        }


class JSONException(InteractionException):
    """
    This is a derivation of InteractionException in that this is used to represent JSON API Exceptions.

    :ivar ErrorFormatter _formatter: The built-in formatter.
    :ivar dict _lookup: A dictionary containing the values from the built-in Enum.
    """

    __slots__ = ("_type", "_lookup", "__type", "_formatter", "kwargs")

    def __init__(self, __type, **kwargs):
        super().__init__(__type, **kwargs)

    @staticmethod
    def lookup() -> dict:
        return {
            0: "Unknown Error.",
            10001: "Unknown Account.",
            10002: "Unknown Application.",
            10003: "Unknown Channel.",
            10004: "Unknown Guild.",
            10005: "Unknown Integration.",
            10006: "Unknown Invite.",
            10007: "Unknown Member.",
            10008: "Unknown Message.",
            10009: "Unknown Overwrite.",
            10010: "Unknown Provider.",
            10011: "Unknown Role.",
            10012: "Unknown Token.",
            10013: "Unknown User.",
            10014: "Unknown Emoji.",
            10015: "Unknown Webhook.",
            10016: "Unknown Webhook Service.",
            10020: "Unknown Session.",
            10026: "Unknown Ban.",
            10027: "Unknown SKU.",
            10028: "Unknown Store Listing.",
            10029: "Unknown Entitlement.",
            10030: "Unknown Team.",
            10031: "Unknown Lobby.",
            10032: "Unknown Branch.",
            10033: "Unknown Store directory layout.",
            10036: "Unknown Redistributable.",
            10038: "Unknown Gift Code.",
            10049: "Unknown Stream.",
            10050: "Unknown Guild boost cooldown.",
            10057: "Unknown Guild template.",
            10059: "Unknown Discovery category.",
            10060: "Unknown Sticker.",
            10062: "Unknown Interaction.",
            10063: "Unknown Application Command.",
            10066: "Unknown Application Command permissions.",
            10067: "Unknown Stage.",
            10068: "Unknown Guild Member Verification Form.",
            10069: "Unknown Guild Welcome Screen.",
            10070: "Unknown Scheduled Event.",
            10071: "Unknown Scheduled Event user.",
            20001: "Bots cannot use this endpoint.",
            20002: "Only bots can use this endpoint.",
            20009: "Explicit content cannot be sent to the desired recipient(s).",
            20012: "You are not authorized to perform this action on this application",
            20016: "This action cannot be performed due to slowmode rate limit.",
            20018: "Only the owner of this account can perform this action",
            20022: "This message cannot be edited due to announcement rate limits.",
            20028: "The channel you are writing has hit the write rate limit",
            20031: "Your Stage topic, server name, server description, or channel names contain words that are not allowed",
            20035: "Guild premium subscription level too low"
            #  TODO: post-v4: finish dict.
        }
