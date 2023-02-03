from typing import TYPE_CHECKING

import interactions.client.const as const
import interactions.models as models
from interactions.models.discord.enums import CommandType

if TYPE_CHECKING:
    from interactions import InteractionCommand, SlashCommand, SlashCommandOption

__all__ = ("deserialize_app_cmds",)


def deserialize_app_cmds(data: list[dict]) -> list["InteractionCommand"]:
    """
    Deserializes the application_commands field of the audit log.

    Args:
        data: The application commands data

    Returns:
        A list of interaction command objects
    """
    out = []
    command_mapping = {
        CommandType.CHAT_INPUT: models.internal.SlashCommand,
        CommandType.USER: models.internal.ContextMenu,
        CommandType.MESSAGE: models.internal.ContextMenu,
    }

    for cmd_dict in data:
        options = cmd_dict.pop("options", [])
        cmd_type = cmd_dict["type"]

        if cmd_type == CommandType.CHAT_INPUT:
            del cmd_dict["type"]
        else:
            del cmd_dict["description"]

        cmd_dict["cmd_id"] = cmd_dict.pop("id")
        cmd_dict["scopes"] = [cmd_dict.pop("guild_id", const.GLOBAL_SCOPE)]

        del cmd_dict["version"]
        del cmd_dict["default_permission"]
        cmd = command_mapping[cmd_type](**cmd_dict)  # type: ignore

        if options:
            if subcommands := deserialize_subcommands(cmd, options):
                out += subcommands
                continue
            cmd.options = deserialize_options(options)

        out.append(cmd)
    return out


def deserialize_subcommands(
    base_cmd: "SlashCommand", options: list[dict], parent_group: dict | None = None
) -> list["SlashCommand"]:
    """
    Deserializes subcommands.

    Args:
        base_cmd: The subcommands base command
        options: The options from the parent
        parent_group: The parent group, if any

    Returns:
        A list of slashcommand (subcommand) objects
    """
    out = []
    for opt in options:
        if opt["type"] == models.internal.OptionType.SUB_COMMAND_GROUP:
            out += deserialize_subcommands(
                base_cmd, opt["options"], {"name": opt["name"], "description": opt["description"]}
            )
        elif opt["type"] == models.internal.OptionType.SUB_COMMAND:
            out.append(
                models.internal.SlashCommand(
                    name=base_cmd.name,
                    description=base_cmd.description,
                    group_name=parent_group["name"] if parent_group else None,
                    group_description=parent_group["description"] if parent_group else None,
                    options=deserialize_options(opt.get("options", [])),
                    sub_cmd_name=opt["name"],
                    sub_cmd_description=opt["description"],
                    default_member_permissions=base_cmd.default_member_permissions,
                    dm_permission=base_cmd.dm_permission,
                    scopes=base_cmd.scopes,
                )
            )
    return out


def deserialize_options(options: list[dict]) -> list["SlashCommandOption"]:
    """
    Deserializes the options of a slash command

    Args:
        options: The list of options provided by discord

    Returns:
        list of SlashCommandOption objects
    """
    return [
        models.internal.SlashCommandOption(**opt)
        for opt in options
        if opt["type"] not in (models.internal.OptionType.SUB_COMMAND_GROUP, models.internal.OptionType.SUB_COMMAND)
    ]
