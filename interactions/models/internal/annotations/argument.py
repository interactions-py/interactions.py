from typing import TYPE_CHECKING

from interactions.client.errors import BadArgument
from interactions.models.internal.context import Context, PrefixedContext
from interactions.models.internal.converters import NoArgumentConverter

__all__ = ("CMD_ARGS", "CMD_AUTHOR", "CMD_BODY", "CMD_CHANNEL")


if TYPE_CHECKING:
    from interactions.models import Member, User, TYPE_MESSAGEABLE_CHANNEL


class CMD_BODY(NoArgumentConverter[str]):
    """
    This argument is for the body of the message.

    IE:

    if `@bot hello how are you?` is sent this argument will be `hello how are you?`
    """

    async def convert(self, context: Context, _) -> str:
        """Returns the body of the message."""
        if not isinstance(context, PrefixedContext):
            raise BadArgument("CMD_BODY can only be used with prefixed commands.")
        return context.content_parameters


class CMD_AUTHOR(NoArgumentConverter):
    """This argument is the author of the context."""

    async def convert(self, context: Context, _) -> "Member | User":
        """Returns the author of the context."""
        return context.author


class CMD_CHANNEL(NoArgumentConverter):
    """This argument is the channel the command was sent in."""

    async def convert(self, context: Context, _) -> "TYPE_MESSAGEABLE_CHANNEL":
        """Returns the channel of the context."""
        return context.channel


class CMD_ARGS(NoArgumentConverter[list[str]]):
    """This argument is all of the arguments sent with this context."""

    @staticmethod
    async def convert(context: Context, _) -> list[str]:
        """Returns the arguments for this context."""
        return context.args
