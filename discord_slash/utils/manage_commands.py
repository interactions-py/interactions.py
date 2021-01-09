import typing
import asyncio
import aiohttp
from ..error import RequestFailure
from ..model import SlashCommandOptionType
from collections.abc import Callable


async def add_slash_command(bot_id,
                            bot_token: str,
                            guild_id,
                            cmd_name: str,
                            description: str,
                            options: list = None):
    """
    A coroutine that sends a slash command add request to Discord API.

    :param bot_id: User ID of the bot.
    :param bot_token: Token of the bot.
    :param guild_id: ID of the guild to add command. Pass `None` to add global command.
    :param cmd_name: Name of the command. Must be 3 or longer and 32 or shorter.
    :param description: Description of the command.
    :param options: List of the function.
    :return: JSON Response of the request.
    :raises: :class:`.error.RequestFailure` - Requesting to Discord API has failed.
    """
    url = f"https://discord.com/api/v8/applications/{bot_id}"
    url += "/commands" if not guild_id else f"/guilds/{guild_id}/commands"
    base = {
        "name": cmd_name,
        "description": description,
        "options": options if options else []
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers={"Authorization": f"Bot {bot_token}"}, json=base) as resp:
            if resp.status == 429:
                _json = await resp.json()
                await asyncio.sleep(_json["retry_after"])
                return await add_slash_command(bot_id, bot_token, guild_id, cmd_name, description, options)
            if not 200 <= resp.status < 300:
                raise RequestFailure(resp.status, await resp.text())
            return await resp.json()


async def remove_slash_command(bot_id,
                               bot_token,
                               guild_id,
                               cmd_id):
    """
    A coroutine that sends a slash command remove request to Discord API.

    :param bot_id: User ID of the bot.
    :param bot_token: Token of the bot.
    :param guild_id: ID of the guild to remove command. Pass `None` to remove global command.
    :param cmd_id: ID of the command.
    :return: Response code of the request.
    :raises: :class:`.error.RequestFailure` - Requesting to Discord API has failed.
    """
    url = f"https://discord.com/api/v8/applications/{bot_id}"
    url += "/commands" if not guild_id else f"/guilds/{guild_id}/commands"
    url += f"/{cmd_id}"
    async with aiohttp.ClientSession() as session:
        async with session.delete(url, headers={"Authorization": f"Bot {bot_token}"}) as resp:
            if resp.status == 429:
                _json = await resp.json()
                await asyncio.sleep(_json["retry_after"])
                return await remove_slash_command(bot_id, bot_token, guild_id, cmd_id)
            if not 200 <= resp.status < 300:
                raise RequestFailure(resp.status, await resp.text())
            return resp.status


async def get_all_commands(bot_id,
                           bot_token,
                           guild_id=None):
    """
    A coroutine that sends a slash command get request to Discord API.

    :param bot_id: User ID of the bot.
    :param bot_token: Token of the bot.
    :param guild_id: ID of the guild to get commands. Pass `None` to get all global commands.
    :return: JSON Response of the request.
    :raises: :class:`.error.RequestFailure` - Requesting to Discord API has failed.
    """
    url = f"https://discord.com/api/v8/applications/{bot_id}"
    url += "/commands" if not guild_id else f"/guilds/{guild_id}/commands"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"Authorization": f"Bot {bot_token}"}) as resp:
            if resp.status == 429:
                _json = await resp.json()
                await asyncio.sleep(_json["retry_after"])
                return await get_all_commands(bot_id, bot_token, guild_id)
            if not 200 <= resp.status < 300:
                raise RequestFailure(resp.status, await resp.text())
            return await resp.json()


async def remove_all_commands(bot_id,
                              bot_token,
                              guild_ids: typing.List[int] = None):
    """
    Remove all slash commands.

    :param bot_id: User ID of the bot.
    :param bot_token: Token of the bot.
    :param guild_ids: List of the guild ID to remove commands. Pass ``None`` to remove only the global commands.
    """

    await remove_all_commands_in(bot_id, bot_token, None)

    for x in guild_ids if guild_ids else []:
        try:
            await remove_all_commands_in(bot_id, bot_token, x)
        except RequestFailure:
            pass


async def remove_all_commands_in(bot_id,
                                 bot_token,
                                 guild_id=None):
    """
    Remove all slash commands in area.

    :param bot_id: User ID of the bot.
    :param bot_token: Token of the bot.
    :param guild_id: ID of the guild to remove commands. Pass `None` to remove all global commands.
    """
    commands = await get_all_commands(
        bot_id,
        bot_token,
        guild_id
    )

    for x in commands:
        await remove_slash_command(
            bot_id,
            bot_token,
            guild_id,
            x['id']
        )


def create_option(name: str,
                  description: str,
                  option_type: int,
                  required: bool,
                  choices: list = None) -> dict:
    """
    Creates option used for creating slash command.

    :param name: Name of the option.
    :param description: Description of the option.
    :param option_type: Type of the option.
    :param required: Whether this option is required.
    :param choices: Choices of the option. Can be empty.
    :return: dict
    """
    return {
        "name": name,
        "description": description,
        "type": option_type,
        "required": required,
        "choices": choices if choices else []
    }


def create_options_from_args(function: Callable, description: str = "No description.") -> list:
    """
    Creates a list of options from the type hints of a command.
    You currently can type hint: str, int, bool, discord.User, discord.Channel, discord.Role

    .. warning::
        This is automatically used if you do not pass any options directly. It is not recommended to use this.

    :param function: The function callable of the command.
    :param description: The default argument description.
    """
    options = []
    for i, (argument, hint) in enumerate(typing.get_type_hints(function).items()):
        if i == 0:  # First element is ctx
            continue

        required = True
        if typing.get_origin(hint) is typing.Union:
            # Make a command argument optional with typing.Optional[type] or typing.Union[type, None]
            args = typing.get_args(hint)
            hint = args[0]
            required = not args[-1] is type(None)

        option_type = SlashCommandOptionType.from_type(hint)  # If no type hint is passed, then defaults to string
        options.append(create_option(argument, description, option_type, required))

    return options


def create_choice(value: str, name: str):
    """
    Creates choices used for creating command option.

    :param value: Value of the choice.
    :param name: Name of the choice.
    :return: dict
    """
    return {
        "value": value,
        "name": name
    }
