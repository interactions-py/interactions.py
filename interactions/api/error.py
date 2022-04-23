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
            20016: "This action cannot be performed due to slow-mode rate limit.",
            20018: "Only the owner of this account can perform this action",
            20022: "This message cannot be edited due to announcement rate limits.",
            20028: "The channel you are writing has hit the write rate limit",
            20031: "Your Stage topic, server name, server description, "
            "or channel names contain words that are not allowed",
            20035: "Guild premium subscription level too low",
            30001: "Maximum number of guilds reached (100)",
            30002: "Maximum number of friends reached (1000)",
            30003: "Maximum number of pins reached for the channel (50)",
            30004: "Maximum number of recipients reached (10)",
            30005: "Maximum number of guild roles reached (250)",
            30007: "Maximum number of webhooks reached (10)",
            30008: "Maximum number of emojis reached",
            30010: "Maximum number of reactions reached (20)",
            30013: "Maximum number of guild channels reached (500)",
            30015: "Maximum number of attachments in a message reached (10)",
            30016: "Maximum number of invites reached (1000)",
            30018: "Maximum number of animated emojis reached",
            30019: "Maximum number of server members reached",
            30030: "Maximum number of server categories has been reached",
            30031: "Guild already has a template",
            30033: "Max number of thread participants has been reached (1000)",
            30035: "Maximum number of bans for non-guild members have been exceeded",
            30037: "Maximum number of bans fetches has been reached",
            30038: "Maximum number of uncompleted guild scheduled events reached (100)",
            30039: "Maximum number of stickers reached",
            30040: "Maximum number of prune requests has been reached. Try again later",
            30042: "Maximum number of guild widget settings updates has been reached. Try again later",
            30046: "Maximum number of edits to messages older than 1 hour reached. Try again later",
            40001: "Unauthorized. Provide a valid token and try again",
            40002: "You need to verify your account in order to perform this action",
            40003: "You are opening direct messages too fast",
            40004: "Send messages has been temporarily disabled",
            40005: "Request entity too large. Try sending something smaller in size",
            40006: "This feature has been temporarily disabled server-side",
            40007: "The user is banned from this guild",
            40032: "Target user is not connected to voice",
            40033: "This message has already been crossposted",
            40041: "An application command with that name already exists",
            40060: "Interaction has already been acknowledged",
            50001: "Missing access",
            50002: "Invalid account type",
            50003: "Cannot execute action on a DM channel",
            50004: "Guild widget disabled",
            50005: "Cannot edit a message authored by another user",
            50006: "Cannot send an empty message",
            50007: "Cannot send messages to this user",
            50008: "Cannot send messages in a non-text channel",
            50009: "Channel verification level is too high for you to gain access",
            50010: "OAuth2 application does not have a bot",
            50011: "OAuth2 application limit reached",
            50012: "Invalid OAuth2 state",
            50013: "You lack permissions to perform that action",
            50014: "Invalid authentication token provided",
            50015: "Note was too long",
            50016: "Provided too few or too many messages to delete. "
            "Must provide at least 2 and fewer than 100 messages to delete",
            50019: "A message can only be pinned to the channel it was sent in",
            50020: "Invite code was either invalid or taken",
            50021: "Cannot execute action on a system message",
            50024: "Cannot execute action on this channel type",
            50025: "Invalid OAuth2 access token provided",
            50026: "Missing required OAuth2 scope",
            50027: "Invalid webhook token provided",
            50028: "Invalid role",
            50033: "Invalid Recipient(s)",
            50034: "A message provided was too old to bulk delete",
            50035: "Invalid form body (returned for both application/json and multipart/form-data bodies),"
            " or invalid Content-Type provided",
            50036: "An invite was accepted to a guild the application's bot is not in",
            50041: "Invalid API version provided",
            50045: "File uploaded exceeds the maximum size",
            50046: "Invalid file uploaded",
            50054: "Cannot self-redeem this gift",
            50055: "Invalid Guild",
            50068: "Invalid message type",
            50070: "Payment source required to redeem gift",
            50074: "Cannot delete a channel required for Community guilds",
            50081: "Invalid sticker sent",
            50083: "Tried to perform an operation on an archived thread, such as editing a "
            "message or adding a user to the thread",
            50084: "Invalid thread notification settings",
            50085: "'before' value is earlier than the thread creation date",
            50086: "Community server channels must be text channels",
            50095: "This server is not available in your location",
            50097: "This server needs monetization enabled in order to perform this action",
            50101: "This server needs more boosts to perform this action",
            50109: "The request body contains invalid JSON.",
            60003: "Two factor is required for this operation",
            80004: "No users with DiscordTag exist",
            90001: "Reaction was blocked",
            130000: "API resource is currently overloaded. Try again a little later",
            150006: "The Stage is already open",
            160002: "Cannot reply without permission to read message history",
            160004: "A thread has already been created for this message",
            160005: "Thread is locked",
            160006: "Maximum number of active threads reached",
            160007: "Maximum number of active announcement threads reached",
            170001: "Invalid JSON for uploaded Lottie file",
            170002: "Uploaded Lotties cannot contain rasterized images such as PNG or JPEG",
            170003: "Sticker maximum framerate exceeded",
            170004: "Sticker frame count exceeds maximum of 1000 frames",
            170005: "Lottie animation maximum dimensions exceeded",
            170006: "Sticker frame rate is either too small or too large",
            170007: "Sticker animation duration exceeds maximum of 5 seconds",
            180000: "Cannot update a finished event",
            180002: "Failed to create stage needed for stage event",
        }
