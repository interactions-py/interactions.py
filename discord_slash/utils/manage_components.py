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
        raise IncorrectFormat("Number of components in one row should be between 1 and 5.")
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


def emoji_to_dict(emoji: typing.Union[discord.Emoji, discord.PartialEmoji, str]) -> dict:
    """
    Converts a default or custom emoji into a partial emoji dict.

    :param emoji: The emoji to convert.
    :type emoji: Union[discord.Emoji, discord.PartialEmoji, str]
    """
    if isinstance(emoji, discord.Emoji):
        emoji = {"name": emoji.name, "id": emoji.id, "animated": emoji.animated}
    elif isinstance(emoji, str):
        emoji = {"name": emoji, "id": None}
    return emoji if emoji else {}


def create_button(style: typing.Union[ButtonStyle, int],
                  label: str = None,
                  emoji: typing.Union[discord.Emoji, discord.PartialEmoji, str] = None,
                  custom_id: str = None,
                  url: str = None,
                  disabled: bool = False) -> dict:
    """
    Creates a button component for use with the ``components`` field. Must be inside an ActionRow to be used (see :meth:`create_actionrow`).

    .. note::
        At least a label or emoji is required for a button. You can have both, but not neither of them.

    :param style: Style of the button. Refer to :class:`ButtonStyle`.
    :type style: Union[ButtonStyle, int]
    :param label: The label of the button.
    :type label: Optional[str]
    :param emoji: The emoji of the button.
    :type emoji: Union[discord.Emoji, discord.PartialEmoji, dict]
    :param custom_id: The custom_id of the button. Needed for non-link buttons.
    :type custom_id: Optional[str]
    :param url: The URL of the button. Needed for link buttons.
    :type url: Optional[str]
    :param disabled: Whether the button is disabled or not. Defaults to `False`.
    :type disabled: bool
    :returns: :class:`dict`
    """
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


def create_select_option(label: str, value: str, emoji=None, description: str = None, default: bool = False):
    """
    Creates an option for select components.

    :param label: The label of the option.
    :param value: The value that the bot will recieve when this option is selected.
    :param emoji: The emoji of the option.
    :param description: A description of the option.
    :param default: Whether or not this is the default option.
    """
    emoji = emoji_to_dict(emoji)

    return {
        "label": label,
        "value": value,
        "description": description,
        "default": default,
        "emoji": emoji
    }


def create_select(options: list[dict], custom_id=None, placeholder=None, min_values=None, max_values=None):
    """
    Creates a select (dropdown) component for use with the ``components`` field. Must be inside an ActionRow to be used (see :meth:`create_actionrow`).

    .. warning::
        Currently, select components are not available for public use, nor have official documentation. The parameters will not be documented at this time.
    """
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


async def wait_for_component(client: discord.Client, component: typing.Union[dict, str], check=None, timeout=None) \
        -> ComponentContext:
    """
    Waits for a component interaction. Only accepts interactions based on the custom ID of the component, and optionally a check function.

    :param client: The client/bot object.
    :type client: :class:`discord.Client`
    :param component: The component dict or custom ID.
    :type component: Union[dict, str]
    :param check: Optional check function. Must take a `ComponentContext` as the first parameter.
    :param timeout: The number of seconds to wait before timing out and raising :exc:`asyncio.TimeoutError`.
    :raises: :exc:`asyncio.TimeoutError`
    """
    def _check(ctx):
        if check and not check(ctx):
            return False
        return (component["custom_id"] if isinstance(component, dict) else component) == ctx.custom_id

    return await client.wait_for("component", check=_check, timeout=timeout)


async def wait_for_any_component(client: discord.Client, message: typing.Union[discord.Message, int],
                                 check=None, timeout=None) -> ComponentContext:
    """
    Waits for any component interaction. Only accepts interactions based on the message ID given and optionally a check function.

    :param client: The client/bot object.
    :type client: :class:`discord.Client`
    :param message: The message object to check for, or the message ID.
    :type message: Union[discord.Message, int]
    :param check: Optional check function. Must take a `ComponentContext` as the first parameter.
    :param timeout: The number of seconds to wait before timing out and raising :exc:`asyncio.TimeoutError`.
    :raises: :exc:`asyncio.TimeoutError`
    """
    def _check(ctx):
        if check and not check(ctx):
            return False
        return (message.id if isinstance(message, discord.Message) else message) == ctx.origin_message_id

    return await client.wait_for("component", check=_check, timeout=timeout)
