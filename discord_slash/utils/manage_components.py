import uuid
import enum
import typing
import discord
from ..error import IncorrectFormat


class ComponentsType(enum.IntEnum):
    actionrow = 1
    button = 2
    select = 3


def create_actionrow(*components: dict) -> dict:
    """
    Creates an ActionRow for message components.
    :param components: Components to go within the ActionRow.
    :return: dict
    """

    return {
        "type": ComponentsType.actionrow,
        "components": components
    }


class ButtonStyle(enum.IntEnum):
    blue = 1
    gray = 2
    grey = 2
    green = 3
    red = 4
    URL = 5


def emoji_to_dict(emoji):
    if isinstance(emoji, discord.Emoji):
        emoji = {"name": emoji.name, "id": emoji.id, "animated": emoji.animated}
    elif isinstance(emoji, str):
        emoji = {"name": emoji, "id": None}
    return emoji if emoji else {}


def create_button(style: int,
                  label: str = None,
                  emoji: typing.Union[discord.Emoji, dict] = None,
                  custom_id: str = None,
                  url: str = None,
                  disabled: bool = False) -> dict:
    if style == 5 and custom_id:
        raise IncorrectFormat("A link button cannot have a `custom_id`!")
    if style == 5 and not url:
        raise IncorrectFormat("A link button must have a `url`!")
    if url and style != 5:
        raise IncorrectFormat("You can't have a URL on a non-link button!")
    if not label and not emoji:
        raise IncorrectFormat("You must have at least a label or emoji on a button.")
    if not custom_id and style != 5:
        custom_id = str(uuid.uuid4())

    emoji = emoji_to_dict(emoji)

    return {
        "type": ComponentsType.button,
        "style": style,
        "label": label if label else "",
        "emoji": emoji,
        "custom_id": custom_id,
        "url": url if url else "",
        "disabled": disabled
    }


def create_select_option(label: str, value: str, emoji=None, description: str = None, default=False):
    emoji = emoji_to_dict(emoji)

    return {
        "label": label,
        "value": value,
        "description": description,
        "default": default,
        "emoji": emoji
    }


def create_select(options: list[dict], custom_id=None, placeholder=None, min_values=None, max_values=None):
    if not len(options) or len(options) > 25:
        raise IncorrectFormat("Options length should be between 1 and 25.")

    return {
        "type": ComponentsType.select,
        "options": options,
        "custom_id": custom_id or str(uuid.uuid4()),
        "placeholder": placeholder or "",
        "min_values": min_values,
        "max_values": max_values,
    }


async def wait_for_component(client, component, check=None, timeout=None):
    def _check(ctx):
        if check and not check(ctx):
            return False
        return component["custom_id"] == ctx.custom_id

    return await client.wait_for("component", check=_check, timeout=timeout)


async def wait_for_any_component(client, message, check=None, timeout=None):
    def _check(ctx):
        if check and not check(ctx):
            return False
        return message.id == ctx.origin_message_id

    return await client.wait_for("component", check=_check, timeout=timeout)

