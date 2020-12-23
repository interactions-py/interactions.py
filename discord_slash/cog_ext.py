import typing
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


def cog_subcommand(*,
                   base,
                   subcommand_group=None,
                   name=None,
                   description: str = None,
                   auto_convert: dict = None,
                   guild_ids: typing.List[int] = None):
    def wrapper(cmd):
        _sub = {
            "func": cmd,
            "name": name,
            "description": description,
            "auto_convert": auto_convert,
            "guild_ids": guild_ids,
        }
        return CogSubcommandObject(_sub, base, name, subcommand_group)
    return wrapper
