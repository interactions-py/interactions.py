from typing import Union

import discord_typings

import interactions.models.discord.components as components
from interactions import ButtonStyle, ChannelType, ComponentType


class UIComponent:
    def __init__(self, row: int):
        self.row = row

    def generate_custom_id(self, *_, **__):
        return None


class Button(components.Button, UIComponent):
    def __init__(
        self,
        *,
        style: ButtonStyle,
        label: str | None = None,
        emoji: "PartialEmoji | None | str" = None,
        custom_id: str = None,
        url: str | None = None,
        disabled: bool = False,
        row: int | None = None,
    ):
        super().__init__(style=style, label=label, emoji=emoji, custom_id=custom_id, url=url, disabled=disabled)
        UIComponent.__init__(self, row)


class BaseSelectMenu(components.BaseSelectMenu, UIComponent):
    def __init__(
        self,
        *,
        placeholder: str | None = None,
        min_values: int = 1,
        max_values: int = 1,
        custom_id: str | None = None,
        disabled: bool = False,
        row: int | None = None,
    ):
        super().__init__(
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            custom_id=custom_id,
            disabled=disabled,
        )
        UIComponent.__init__(self, row)


class StringSelectMenu(components.StringSelectMenu, UIComponent):
    def __init__(
        self,
        *options: components.StringSelectOption | str | discord_typings.SelectMenuOptionData,
        placeholder: str | None = None,
        min_values: int = 1,
        max_values: int = 1,
        custom_id: str | None = None,
        disabled: bool = False,
        row: int | None = None,
    ):
        super().__init__(
            *options,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            custom_id=custom_id,
            disabled=disabled,
        )
        UIComponent.__init__(self, row)


class UserSelectMenu(components.UserSelectMenu, UIComponent):
    def __init__(
        self,
        *,
        placeholder: str | None = None,
        min_values: int = 1,
        max_values: int = 1,
        custom_id: str | None = None,
        disabled: bool = False,
        row: int | None = None,
    ) -> None:
        super().__init__(
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            custom_id=custom_id,
            disabled=disabled,
        )
        UIComponent.__init__(self, row)


class RoleSelectMenu(components.RoleSelectMenu, UIComponent):
    def __init__(
        self,
        *,
        placeholder: str | None = None,
        min_values: int = 1,
        max_values: int = 1,
        custom_id: str | None = None,
        disabled: bool = False,
        row: int | None = None,
    ) -> None:
        super().__init__(
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            custom_id=custom_id,
            disabled=disabled,
        )
        UIComponent.__init__(self, row)


class MentionableSelectMenu(components.MentionableSelectMenu, UIComponent):
    def __init__(
        self,
        *,
        placeholder: str | None = None,
        min_values: int = 1,
        max_values: int = 1,
        custom_id: str | None = None,
        disabled: bool = False,
        row: int | None = None,
    ) -> None:
        super().__init__(
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            custom_id=custom_id,
            disabled=disabled,
        )
        UIComponent.__init__(self, row)


class ChannelSelectMenu(components.ChannelSelectMenu, UIComponent):
    def __init__(
        self,
        *,
        channel_types: list[ChannelType] | None = None,
        placeholder: str | None = None,
        min_values: int = 1,
        max_values: int = 1,
        custom_id: str | None = None,
        disabled: bool = False,
        row: int | None = None,
    ) -> None:
        super().__init__(
            channel_types=channel_types,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            custom_id=custom_id,
            disabled=disabled,
        )
        UIComponent.__init__(self, row)


def get_component_weight(component: Union[components.BaseComponent, UIComponent]) -> int:
    """Get the weight of a component."""
    lookup = {
        ComponentType.BUTTON: 1,
        ComponentType.STRING_SELECT: 5,
        ComponentType.USER_SELECT: 5,
        ComponentType.CHANNEL_SELECT: 5,
        ComponentType.ROLE_SELECT: 5,
        ComponentType.MENTIONABLE_SELECT: 5,
    }
    return lookup[component.type]


__all__ = (
    "Button",
    "BaseSelectMenu",
    "StringSelectMenu",
    "UserSelectMenu",
    "RoleSelectMenu",
    "ChannelSelectMenu",
    "MentionableSelectMenu",
    "UIComponent",
    "get_component_weight",
)
