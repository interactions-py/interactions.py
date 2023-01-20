from typing import TYPE_CHECKING
from interactions.models.discord.user import Member, User

from interactions.models.internal.context import BaseContext
from interactions.models.internal.converters import NoArgumentConverter

__all__ = ("CMD_ARGS", "CMD_AUTHOR", "CMD_CHANNEL")


if TYPE_CHECKING:
    from interactions.models import TYPE_MESSAGEABLE_CHANNEL


class CMD_AUTHOR(NoArgumentConverter):
    """This argument is the author of the context."""

    async def convert(self, context: BaseContext, _) -> "Member | User":
        """Returns the author of the context."""
        return context.author


class CMD_CHANNEL(NoArgumentConverter):
    """This argument is the channel the command was sent in."""

    async def convert(self, context: BaseContext, _) -> "TYPE_MESSAGEABLE_CHANNEL":
        """Returns the channel of the context."""
        return context.channel


class CMD_ARGS(NoArgumentConverter[list[str]]):
    """This argument is all the arguments sent with this context."""

    @staticmethod
    async def convert(context: BaseContext, _) -> list[str]:
        """Returns the arguments for this context."""
        return context.args
