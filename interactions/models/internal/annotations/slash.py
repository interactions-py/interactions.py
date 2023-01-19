from typing import TYPE_CHECKING, List, Optional, Type, Union

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
    from interactions.models.discord import (
        Attachment,
        BaseChannel,
        ChannelTypes,
        Member,
        Role,
        User,
    )
    from interactions.models.internal import SlashCommandChoice


def slash_str_option(
    description: str,
    required: bool = False,
    autocomplete: bool = False,
    choices: List[Union["SlashCommandChoice", dict]] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
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

    """
    option = SlashCommandOption(
        name="placeholder",
        description=description,
        required=required,
        autocomplete=autocomplete,
        choices=choices or [],
        max_length=max_length,
        min_length=min_length,
        type=models.OptionTypes.STRING,
    )
    return option  # type: ignore


def slash_float_option(
    description: str,
    required: bool = False,
    autocomplete: bool = False,
    choices: List[Union["SlashCommandChoice", dict]] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
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

    """
    option = SlashCommandOption(
        name="placeholder",
        description=description,
        required=required,
        autocomplete=autocomplete,
        choices=choices or [],
        max_value=max_value,
        min_value=min_value,
        type=models.OptionTypes.NUMBER,
    )
    return option  # type: ignore


def slash_int_option(
    description: str,
    required: bool = False,
    autocomplete: bool = False,
    choices: List[Union["SlashCommandChoice", dict]] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
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

    """
    option = SlashCommandOption(
        name="placeholder",
        description=description,
        required=required,
        autocomplete=autocomplete,
        choices=choices or [],
        max_value=max_value,
        min_value=min_value,
        type=models.OptionTypes.INTEGER,
    )
    return option  # type: ignore


def slash_bool_option(
    description: str,
    required: bool = False,
) -> Type[bool]:
    """
    Annotates an argument as a boolean type slash command option.

    Args:
        description: The description of your option
        required: Is this option required?

    """
    option = SlashCommandOption(
        name="placeholder",
        description=description,
        required=required,
        type=models.OptionTypes.BOOLEAN,
    )
    return option  # type: ignore


def slash_user_option(
    description: str,
    required: bool = False,
    autocomplete: bool = False,
) -> Type[Union["User", "Member"]]:
    """
    Annotates an argument as a user type slash command option.

    Args:
        description: The description of your option
        required: Is this option required?
        autocomplete: Use autocomplete for this option

    """
    option = SlashCommandOption(
        name="placeholder",
        description=description,
        required=required,
        autocomplete=autocomplete,
        type=models.OptionTypes.USER,
    )
    return option  # type: ignore


def slash_channel_option(
    description: str,
    required: bool = False,
    autocomplete: bool = False,
    choices: List[Union["SlashCommandChoice", dict]] = None,
    channel_types: Optional[list[Union["ChannelTypes", int]]] = None,
) -> Type["BaseChannel"]:
    """
    Annotates an argument as a channel type slash command option.

    Args:
        description: The description of your option
        required: Is this option required?
        autocomplete: Use autocomplete for this option
        choices: The choices allowed by this command
        channel_types: The types of channel allowed by this option

    """
    option = SlashCommandOption(
        name="placeholder",
        description=description,
        required=required,
        autocomplete=autocomplete,
        choices=choices or [],
        channel_types=channel_types,
        type=models.OptionTypes.CHANNEL,
    )
    return option  # type: ignore


def slash_role_option(
    description: str,
    required: bool = False,
    autocomplete: bool = False,
    choices: List[Union["SlashCommandChoice", dict]] = None,
) -> Type["Role"]:
    """
    Annotates an argument as a role type slash command option.

    Args:
        description: The description of your option
        required: Is this option required?
        autocomplete: Use autocomplete for this option
        choices: The choices allowed by this command

    """
    option = SlashCommandOption(
        name="placeholder",
        description=description,
        required=required,
        autocomplete=autocomplete,
        choices=choices or [],
        type=models.OptionTypes.ROLE,
    )
    return option  # type: ignore


def slash_mentionable_option(
    description: str,
    required: bool = False,
    autocomplete: bool = False,
    choices: List[Union["SlashCommandChoice", dict]] = None,
) -> Type[Union["Role", "BaseChannel", "User", "Member"]]:
    """
    Annotates an argument as a mentionable type slash command option.

    Args:
        description: The description of your option
        required: Is this option required?
        autocomplete: Use autocomplete for this option
        choices: The choices allowed by this command

    """
    option = SlashCommandOption(
        name="placeholder",
        description=description,
        required=required,
        autocomplete=autocomplete,
        choices=choices or [],
        type=models.OptionTypes.MENTIONABLE,
    )
    return option  # type: ignore


def slash_attachment_option(
    description: str,
    required: bool = False,
) -> Type["Attachment"]:
    """
    Annotates an argument as an attachment type slash command option.

    Args:
        description: The description of your option
        required: Is this option required?

    """
    option = SlashCommandOption(
        name="placeholder",
        description=description,
        required=required,
        type=models.OptionTypes.ATTACHMENT,
    )

    return option  # type: ignore
