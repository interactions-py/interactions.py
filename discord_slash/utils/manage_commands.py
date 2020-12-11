import aiohttp


async def add_slash_command(bot_id,
                            bot_token: str,
                            guild_id,
                            cmd_name: str,
                            description: str,
                            options: list = None):
    url = f"https://discord.com/api/v8/applications/{bot_id}"
    url += "/commands" if guild_id else f"/guilds/{guild_id}/commands"
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
    url = f"https://discord.com/api/v8/applications/{bot_id}"
    url += "/commands" if guild_id else f"/guilds/{guild_id}/commands"
    url += f"/{cmd_id}"
    async with aiohttp.ClientSession() as session:
        async with session.delete(url, headers={"Authorization": f"Bot {bot_token}"}) as resp:
            return resp.status


def create_option(name: str,
                  description: str,
                  option_type: int,
                  required: bool,
                  choices: list = None):
    return {
        "name": name,
        "description": description,
        "type": option_type,
        "required": required,
        "choices": choices if choices else []
    }


def create_choices(value: str, description: str):
    return {
        "value": value,
        "name": description
    }
