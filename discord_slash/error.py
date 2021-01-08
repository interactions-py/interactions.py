class SlashCommandError(Exception):
    """
    All exceptions of this extension can be captured with this.
    Note that discord.py doesn't trigger `on_command_error` event.
    """


class RequestFailure(SlashCommandError):
    """
    Request to Discord API has failed.

    .. note::
        Since release ``1.0.8``, this is only used at :mod:`.utils.manage_commands`. :class:`.http.SlashCommandRequest` uses
        exception from discord.py such as :class:`discord.HTTPException`.

    :ivar status: Status code of failed response.
    :ivar msg: Message of failed response.
    """
    def __init__(self, status: int, msg: str):
        self.status = status
        self.msg = msg
        super().__init__(f"Request failed with resp: {self.status} | {self.msg}")


class IncorrectFormat(SlashCommandError):
    """
    Some formats are incorrect. See Discord API DOCS for proper format.
    """


class DuplicateCommand(SlashCommandError):
    """
    There is a duplicate command name.
    """
    def __init__(self, name: str):
        super().__init__(f"Duplicate command name detected: {name}")
