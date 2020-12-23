import typing
from discord.ext import commands
from .model import CogCommandObject, CogSubcommandObject


def cog_slash(*,
              name: str = None,
              description: str = None,
              auto_convert: dict = None,
              guild_ids: typing.List[int] = None,
              options: typing.List[dict] = None):
    def wrapper(cmd):
        _cmd = {
            "func": cmd,
            "description": description if description else "No description.",
            "auto_convert": auto_convert,
            "guild_ids": guild_ids,
            "api_options": options if options else [],
            "has_subcommands": False
        }
        return CogCommandObject(name, _cmd)
    return wrapper


def register_cog_slash(cls):
    func_list = [getattr(cls, x) for x in dir(cls)]
    return [x for x in func_list if isinstance(x, CogCommandObject) or isinstance(x, CogSubcommandObject)]
