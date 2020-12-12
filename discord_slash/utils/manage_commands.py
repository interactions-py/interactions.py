import aiohttp


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
    """
    url = f"https://discord.com/api/v8/applications/{bot_id}"
    url += "/commands" if not guild_id else f"/guilds/{guild_id}/commands"
    url += f"/{cmd_id}"
    async with aiohttp.ClientSession() as session:
        async with session.delete(url, headers={"Authorization": f"Bot {bot_token}"}) as resp:
            return resp.status


def create_option(name: str,
                  description: str,
                  option_type: int,
                  required: bool,
                  choices: list = None) -> dict:
    """
    Creates option used for creating slash command.

    :param name: Name of the option.
    :param description: Descrption of the option.
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
