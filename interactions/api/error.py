# Normal libraries
from enum import IntEnum
from string import Formatter
from typing import Any, Optional, Union


class ErrorFormatter(Formatter):
    # Need this formatter? Maybe as a starting point, but it's fine either or.
    def get_value(self, key, args, kwargs) -> Any:
        if not isinstance(key, str):
            return Formatter.get_value(self, key=key, args=args, kwargs=kwargs)
        try:
            return kwargs[key]
        except KeyError:
            return key


class InteractionException(Exception):
    """
    Exception class for Interactions.

    .. note::
        This is a WIP. This isn't meant to be used yet, this is a baseline,
        and for extensive testing/review before integration.
        Likewise, this will show the concepts before use, and will be refined when time goes on.

    :ivar _formatter: The built in formatter.
    :ivar _lookup: A dictionary containing the values from the built-in Enum.

    """

    __slots__ = ("__type", "_formatter", "kwargs")
    __type: Optional[Union[int, IntEnum]]
    _formatter: ErrorFormatter

    def __init__(self, __type: Optional[Union[int, IntEnum]] = 0, **kwargs):
        """
        Instantiates the BaseInteractionException class. Upon instantiation, it will print out an error message.
        This is not meant to be used as an object-to-variable declaration,
        this is used to cause an Exception to be thrown.

        .. note::
            (given if 3 is "DUPLICATE_COMMAND" and with the right enum import, it will display 3 as the error code.)
            Example:

            >>> raise InteractionException(2, message="msg")
            Exception raised: "msg" (error 2)

            >>> raise InteractionException(Default_Error_Enum.DUPLICATE_COMMAND)  # noqa
            Exception raised: Duplicate command name. (error 3)

        :param __type: Type of error. This is decided from an IntEnum, which gives readable error messages instead of
        typical error codes. Subclasses of this class works fine, and so does regular integers.
        :type __type: Optional[Union[int, IntEnum]]

        :param kwargs: Any additional keyword arguments.
        :type **kwargs: dict

        """

        self._type = __type
        self.kwargs = kwargs
        self._formatter = ErrorFormatter()
        self._lookup = self.lookup()

        self.error()  # On invocation of the object, it should call the exception.

    # The current layout is that it uses the type, and any arguments parsed to generate readable exceptions.

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
        _err_val = None

        if issubclass(type(self._type), IntEnum):
            _err_val = self.type.name
            _err_rep = self.type.value
        elif type(self.type) == int:
            _err_rep = self.type
        else:  # unidentifiable.
            _err_rep = 0

        _err_msg = _default_err_msg = "Error code: {_err_rep}"

        if self.kwargs != {} and "message" in self.kwargs.keys():
            _err_msg = self.kwargs["message"]  # If there's a `message=`, replace it.

        # We add, for formatting, the error code for kwargs.
        self.kwargs["_err_rep"] = _err_rep  #

        # Then cause the exception to occur. This requires, if overriding the message, "_err_rep" as a required
        # format brace. This is necessary to scale, and more importantly, to diagnose.

        # message= should be given when it's needed, i.e. API request failures

        lookup_str = self._lookup[_err_rep] if _err_rep in self._lookup.keys() else _err_val
        _lookup_str = lookup_str if _err_rep <= max(self._lookup.keys()) else self._lookup[0]
        # Defaults to Unknown error print if the error code is undefined.
        custom_err_str = (
            self._formatter.format(_err_msg, **self.kwargs)
            if "_err_rep" in _err_msg
            else self._formatter.format(_err_msg + _default_err_msg + " ", **self.kwargs)
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
            f"{f'{lookup_str} ' if _err_val is not None else f'{_lookup_str if _err_rep > max(self._lookup.keys()) else lookup_str} '}{custom_err_str}"
        )


class GatewayException(InteractionException):
    """
    This is a derivation of InteractionException in that this is used to represent Gateway closing OP codes.

    :ivar _formatter: The built in formatter.
    :ivar _lookup: A dictionary containing the values from the built-in Enum.
    """

    __slots__ = ("__type", "_formatter", "kwargs")
    __type: Optional[Union[int, IntEnum]]
    _formatter: ErrorFormatter

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


class ClientException(InteractionException):
    """
    This is a derivation of InteractionException in that this is used to represent specialized errors handed back from the client.

    :ivar _formatter: The built in formatter.
    """

    __slots__ = ("__type", "_formatter", "kwargs")
    _formatter: ErrorFormatter

    def __init__(self, __type=0, **kwargs):
        super().__init__(__type, **kwargs)
