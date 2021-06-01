import uuid
import enum
import typing
import discord
from ..context import ComponentContext
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
    if not components or len(components) > 5:
        raise IncorrectFormat("Number of components in one row should be between 1 and 25.")
    if ComponentsType.select in [component["type"] for component in components] and len(components) > 1:
        raise IncorrectFormat("Action row must have only one select component and nothing else")

    return {
        "type": ComponentsType.actionrow,
        "components": components
    }


class ButtonStyle(enum.IntEnum):
    blue = 1
    blurple = 1
    gray = 2
    grey = 2
    green = 3
    red = 4
    URL = 5

    primary = 1
    secondary = 2
    success = 3
    danger = 4


def emoji_to_dict(emoji):
    if isinstance(emoji, discord.Emoji):
        emoji = {"name": emoji.name, "id": emoji.id, "animated": emoji.animated}
    elif isinstance(emoji, str):
        emoji = {"name": emoji, "id": None}
    return emoji if emoji else {}


def create_button(style: ButtonStyle,
                  label: str = None,
                  emoji: typing.Union[discord.Emoji, dict] = None,
                  custom_id: str = None,
                  url: str = None,
                  disabled: bool = False) -> dict:
    if style == ButtonStyle.URL:
        if custom_id:
            raise IncorrectFormat("A link button cannot have a `custom_id`!")
        if not url:
            raise IncorrectFormat("A link button must have a `url`!")
    elif url:
        raise IncorrectFormat("You can't have a URL on a non-link button!")

    if not label and not emoji:
        raise IncorrectFormat("You must have at least a label or emoji on a button.")

    emoji = emoji_to_dict(emoji)

    data = {
        "type": ComponentsType.button,
        "style": style,
    }

    if label:
        data["label"] = label
    if emoji:
        data["emoji"] = emoji
    if disabled:
        data["disabled"] = disabled

    if style == ButtonStyle.URL:
        data["url"] = url
    else:
        data["custom_id"] = custom_id or str(uuid.uuid4())

    return data


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


async def wait_for_component(client, component, check=None, timeout=None) -> ComponentContext:
    def _check(ctx):
        if check and not check(ctx):
            return False
        return component["custom_id"] == ctx.custom_id

    return await client.wait_for("component", check=_check, timeout=timeout)


async def wait_for_any_component(client, message, check=None, timeout=None) -> ComponentContext:
    def _check(ctx):
        if check and not check(ctx):
            return False
        return message.id == ctx.origin_message_id

    return await client.wait_for("component", check=_check, timeout=timeout)

