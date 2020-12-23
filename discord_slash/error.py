class SlashCommandError(Exception):
    """
    All exceptions of this extension can be captured with this.
    Note that discord.py doesn't trigger `on_command_error` event.
    """
    pass


class RequestFailure(SlashCommandError):
    """
    Request to Discord API has failed.

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
    def __init__(self, msg: str):
        super().__init__(msg)


class DuplicateCommand(SlashCommandError):
    """
    There is a duplicate command name.
    """
    def __init__(self, name: str):
        super().__init__(f"Duplicate command name detected: {name}")
