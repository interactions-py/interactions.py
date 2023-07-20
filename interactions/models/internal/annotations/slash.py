from typing import Union, List, Optional, Type, TYPE_CHECKING

import interactions.models as models
from interactions.models.internal.application_commands import SlashCommandOption

__all__ = (
    "slash_attachment_option",
    "slash_bool_option",
    "slash_channel_option",
    "slash_float_option",
    "slash_int_option",
    "slash_mentionable_option",
    "slash_role_option",
    "slash_str_option",
    "slash_user_option",
)


if TYPE_CHECKING:
    from interactions.models.internal import SlashCommandChoice
    from interactions.models.discord import (
        User,
        Member,
        Role,
        BaseChannel,
        ChannelType,
        Attachment,
    )


def slash_str_option(
    description: str,
    required: bool = False,
    autocomplete: bool = False,
    choices: List[Union["SlashCommandChoice", dict]] | None = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    name: Optional[str] = None,
) -> Type[str]:
    """
    Annotates an argument as a string type slash command option.

    Args:
        description: The description of your option
        required: Is this option required?
        autocomplete: Use autocomplete for this option
        choices: The choices allowed by this command
        min_length: The minimum length of text a user can input.
        max_length: The maximum length of text a user can input.
        name: The name of the option. Defaults to the name of the argument

    """
    return SlashCommandOption(
        name=name,
        description=description,
        required=required,
        autocomplete=autocomplete,
        choices=choices or [],
        max_length=max_length,
        min_length=min_length,
        type=models.OptionType.STRING,
    )


def slash_float_option(
    description: str,
    required: bool = False,
    autocomplete: bool = False,
    choices: List[Union["SlashCommandChoice", dict]] | None = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    name: Optional[str] = None,
) -> Type[float]:
    """
    Annotates an argument as a float type slash command option.

    Args:
        description: The description of your option
        required: Is this option required?
        autocomplete: Use autocomplete for this option
        choices: The choices allowed by this command
        min_value: The minimum number allowed
        max_value: The maximum number allowed
        name: The name of the option. Defaults to the name of the argument

    """
    return SlashCommandOption(
        name=name,
        description=description,
        required=required,
        autocomplete=autocomplete,
        choices=choices or [],
        max_value=max_value,
        min_value=min_value,
        type=models.OptionType.NUMBER,
    )


def slash_int_option(
    description: str,
    required: bool = False,
    autocomplete: bool = False,
    choices: List[Union["SlashCommandChoice", dict]] | None = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    name: Optional[str] = None,
) -> Type[int]:
    """
    Annotates an argument as a integer type slash command option.

    Args:
        description: The description of your option
        required: Is this option required?
        autocomplete: Use autocomplete for this option
        choices: The choices allowed by this command
        min_value: The minimum number allowed
        max_value: The maximum number allowed
        name: The name of the option. Defaults to the name of the argument

    """
    return SlashCommandOption(
        name=name,
        description=description,
        required=required,
        autocomplete=autocomplete,
        choices=choices or [],
        max_value=max_value,
        min_value=min_value,
        type=models.OptionType.INTEGER,
    )


def slash_bool_option(
    description: str,
    required: bool = False,
    name: Optional[str] = None,
) -> Type[bool]:
    """
    Annotates an argument as a boolean type slash command option.

    Args:
        description: The description of your option
        required: Is this option required?
        name: The name of the option. Defaults to the name of the argument

    """
    return SlashCommandOption(
        name=name,
        description=description,
        required=required,
        type=models.OptionType.BOOLEAN,
    )


def slash_user_option(
    description: str,
    required: bool = False,
    autocomplete: bool = False,
    name: Optional[str] = None,
) -> Type[Union["User", "Member"]]:
    """
    Annotates an argument as a user type slash command option.

    Args:
        description: The description of your option
        required: Is this option required?
        autocomplete: Use autocomplete for this option
        name: The name of the option. Defaults to the name of the argument

    """
    return SlashCommandOption(
        name=name,
        description=description,
        required=required,
        autocomplete=autocomplete,
        type=models.OptionType.USER,
    )


def slash_channel_option(
    description: str,
    required: bool = False,
    autocomplete: bool = False,
    choices: List[Union["SlashCommandChoice", dict]] | None = None,
    channel_types: Optional[list[Union["ChannelType", int]]] = None,
    name: Optional[str] = None,
) -> Type["BaseChannel"]:
    """
    Annotates an argument as a channel type slash command option.

    Args:
        description: The description of your option
        required: Is this option required?
        autocomplete: Use autocomplete for this option
        choices: The choices allowed by this command
        channel_types: The types of channel allowed by this option
        name: The name of the option. Defaults to the name of the argument

    """
    return SlashCommandOption(
        name=name,
        description=description,
        required=required,
        autocomplete=autocomplete,
        choices=choices or [],
        channel_types=channel_types,
        type=models.OptionType.CHANNEL,
    )


def slash_role_option(
    description: str,
    required: bool = False,
    autocomplete: bool = False,
    choices: List[Union["SlashCommandChoice", dict]] | None = None,
    name: Optional[str] = None,
) -> Type["Role"]:
    """
    Annotates an argument as a role type slash command option.

    Args:
        description: The description of your option
        required: Is this option required?
        autocomplete: Use autocomplete for this option
        choices: The choices allowed by this command
        name: The name of the option. Defaults to the name of the argument

    """
    return SlashCommandOption(
        name=name,
        description=description,
        required=required,
        autocomplete=autocomplete,
        choices=choices or [],
        type=models.OptionType.ROLE,
    )


def slash_mentionable_option(
    description: str,
    required: bool = False,
    autocomplete: bool = False,
    choices: List[Union["SlashCommandChoice", dict]] | None = None,
    name: Optional[str] = None,
) -> Type[Union["Role", "BaseChannel", "User", "Member"]]:
    """
    Annotates an argument as a mentionable type slash command option.

    Args:
        description: The description of your option
        required: Is this option required?
        autocomplete: Use autocomplete for this option
        choices: The choices allowed by this command
        name: The name of the option. Defaults to the name of the argument

    """
    return SlashCommandOption(
        name=name,
        description=description,
        required=required,
        autocomplete=autocomplete,
        choices=choices or [],
        type=models.OptionType.MENTIONABLE,
    )


def slash_attachment_option(
    description: str,
    required: bool = False,
    name: Optional[str] = None,
) -> Type["Attachment"]:
    """
    Annotates an argument as an attachment type slash command option.

    Args:
        description: The description of your option
        required: Is this option required?
        name: The name of the option. Defaults to the name of the argument

    """
    return SlashCommandOption(
        name=name,
        description=description,
        required=required,
        type=models.OptionType.ATTACHMENT,
    )
