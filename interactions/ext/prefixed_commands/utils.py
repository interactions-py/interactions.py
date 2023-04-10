from typing import Callable, Any, Coroutine

from interactions.client.client import Client
from interactions.models.discord.message import Message

__all__ = ("when_mentioned", "when_mentioned_or")


async def when_mentioned(bot: Client, _) -> list[str]:
    """
    Returns a list of the bot's mentions.

    Returns:
        A list of the bot's possible mentions.
    """
    return [f"<@{bot.user.id}> ", f"<@!{bot.user.id}> "]  # type: ignore


def when_mentioned_or(
    *prefixes: str,
) -> Callable[[Client, Message], Coroutine[Any, Any, list[str]]]:
    """
    Returns a list of the bot's mentions plus whatever prefixes are provided.

    This is intended to be used with initializing prefixed commands. If you wish to use
    it in your own function, you will need to do something similar to
    `await when_mentioned_or(*prefixes)(bot, msg)`.

    Args:
        prefixes: Prefixes to include alongside mentions.

    Returns:
        A list of the bot's mentions plus whatever prefixes are provided.
    """

    async def _new_mention(bot: Client, _) -> list[str]:
        return (await when_mentioned(bot, _)) + list(prefixes)

    return _new_mention
