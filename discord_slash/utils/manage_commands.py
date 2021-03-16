import typing
import inspect
import asyncio
import aiohttp
from ..error import RequestFailure, IncorrectType
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
        "options": options or []
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

    for x in guild_ids or []:
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
                  option_type: typing.Union[int, type],
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

    .. note::
        An option with ``required=False`` will not pass anything to the command function if the user doesn't pass that option when invoking the command.
        You must set the the relevant argument's function to a default argument, eg ``argname = None``.

    .. note::
        ``choices`` must either be a list of `option type dicts <https://discord.com/developers/docs/interactions/slash-commands#applicationcommandoptionchoice>`_
        or a list of single string values. 
    """
    if not isinstance(option_type, int) or isinstance(option_type, bool): #Bool values are a subclass of int
        original_type = option_type
        option_type = SlashCommandOptionType.from_type(original_type)
        if option_type is None:
            raise IncorrectType(f"The type {original_type} is not recognized as a type that Discord accepts for slash commands.")
    choices = choices or []
    choices = [choice if isinstance(choice, dict) else {"name": choice, "value": choice} for choice in choices]
    return {
        "name": name,
        "description": description,
        "type": option_type,
        "required": required,
        "choices": choices
    }


def generate_options(function: Callable, description: str = "No description.", connector: dict = None) -> list:
    """
    Generates a list of options from the type hints of a command.
    You currently can type hint: str, int, bool, discord.User, discord.Channel, discord.Role

    .. warning::
        This is automatically used if you do not pass any options directly. It is not recommended to use this.

    :param function: The function callable of the command.
    :param description: The default argument description.
    :param connector: Kwargs connector of the command.
    """
    options = []
    if connector:
        connector = {y: x for x, y in connector.items()} # Flip connector.
    params = iter(inspect.signature(function).parameters.values())
    if next(params).name in ("self", "cls"):
        # Skip 1. (+ 2.) parameter, self/cls and ctx
        next(params)

    for param in params:
        required = True
        if isinstance(param.annotation, str):
            # if from __future__ import annotations, then annotations are strings and should be converted back to types
            param = param.replace(annotation=eval(param.annotation, function.__globals__))

        if param.default is not inspect._empty:
            required = False
        elif getattr(param.annotation, "__origin__", None) is typing.Union:
            # Make a command argument optional with typing.Optional[type] or typing.Union[type, None]
            args = getattr(param.annotation, "__args__", None)
            if args:
                param = param.replace(annotation=args[0])
                required = not args[-1] is type(None)

        option_type = SlashCommandOptionType.from_type(param.annotation) or SlashCommandOptionType.STRING
        name = param.name if not connector else connector[param.name]
        options.append(create_option(name, description or "No Description.", option_type, required))

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
