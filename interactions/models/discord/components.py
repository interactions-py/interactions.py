import uuid
from typing import Any, Dict, Iterator, List, Optional, Sequence, TYPE_CHECKING, Union

import attrs

from interactions.client.const import SELECTS_MAX_OPTIONS, SELECT_MAX_NAME_LENGTH, ACTION_ROW_MAX_ITEMS, MISSING
from interactions.client.mixins.serialization import DictSerializationMixin
from interactions.client.utils import list_converter
from interactions.client.utils.attr_utils import str_validator
from interactions.client.utils.serializer import export_converter
from interactions.models.discord.emoji import process_emoji
from interactions.models.discord.enums import ButtonStyles, ComponentTypes, ChannelTypes

if TYPE_CHECKING:
    from interactions.models.discord.emoji import PartialEmoji

__all__ = (
    "BaseComponent",
    "InteractiveComponent",
    "Button",
    "SelectOption",
    "StringSelectMenu",
    "UserSelectMenu",
    "RoleSelectMenu",
    "MentionableSelectMenu",
    "ChannelSelectMenu",
    "ActionRow",
    "process_components",
    "spread_to_rows",
    "get_components_ids",
    "TYPE_ALL_COMPONENT",
    "TYPE_COMPONENT_MAPPING",
)


class BaseComponent(DictSerializationMixin):
    """
    A base component class.

    !!! Warning
        This should never be instantiated.

    """

    def __init__(self) -> None:
        raise NotImplementedError

    @classmethod
    def from_dict_factory(cls, data: dict) -> "TYPE_ALL_COMPONENT":
        data.pop("hash", None)  # Zero clue why discord sometimes include a hash attribute...

        component_type = data.pop("type", None)
        component_class = TYPE_COMPONENT_MAPPING.get(component_type, None)
        if not component_class:
            raise TypeError(f"Unsupported component type for {data} ({component_type}), please consult the docs.")

        return component_class.from_dict(data)


@attrs.define(eq=False, order=False, hash=False, slots=False)
class InteractiveComponent(BaseComponent):
    """
    A base interactive component class.

    !!! Warning
        This should never be instantiated.

    """

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, dict):
            other = BaseComponent.from_dict_factory(other)
            return self.custom_id == other.custom_id and self.type == other.type
        return False


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class Button(InteractiveComponent):
    """
    Represents a discord ui button.

    Attributes:
        style optional[ButtonStyles, int]: Buttons come in a variety of styles to convey different types of actions.
        label optional[str]: The text that appears on the button, max 80 characters.
        emoji optional[Union[PartialEmoji, dict, str]]: The emoji that appears on the button.
        custom_id Optional[str]: A developer-defined identifier for the button, max 100 characters.
        url Optional[str]: A url for link-style buttons.
        disabled bool: Disable the button and make it not interactable, default false.

    """

    style: Union[ButtonStyles, int] = attrs.field(repr=True)
    label: Optional[str] = attrs.field(repr=False, default=None)
    emoji: Optional[Union["PartialEmoji", dict, str]] = attrs.field(
        repr=True, default=None, metadata=export_converter(process_emoji)
    )
    custom_id: Optional[str] = attrs.field(repr=True, default=MISSING, validator=str_validator)
    url: Optional[str] = attrs.field(repr=True, default=None)
    disabled: bool = attrs.field(repr=True, default=False)
    type: Union[ComponentTypes, int] = attrs.field(
        repr=True, default=ComponentTypes.BUTTON, init=False, on_setattr=attrs.setters.frozen
    )

    @style.validator
    def _style_validator(self, attribute: str, value: int) -> None:
        if not isinstance(value, ButtonStyles) and value not in ButtonStyles.__members__.values():
            raise ValueError(f'Button style type of "{value}" not recognized, please consult the docs.')

    def __attrs_post_init__(self) -> None:
        if self.style != ButtonStyles.URL:
            # handle adding a custom id to any button that requires a custom id
            if self.custom_id is MISSING:
                self.custom_id = str(uuid.uuid4())

    def _check_object(self) -> None:
        if self.style == ButtonStyles.URL:
            if self.custom_id not in (None, MISSING):
                raise TypeError("A link button cannot have a `custom_id`!")
            if not self.url:
                raise TypeError("A link button must have a `url`!")
        else:
            if self.url:
                raise TypeError("You can't have a URL on a non-link button!")

        if not self.label and not self.emoji:
            raise TypeError("You must have at least a label or emoji on a button.")


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class SelectOption(BaseComponent):
    """
    Represents a select option.

    Attributes:
        label str: The label (max 80 characters)
        value str: The value of the select, this is whats sent to your bot
        description Optional[str]: A description of this option
        emoji Optional[Union[PartialEmoji, dict, str]: An emoji to show in this select option
        default bool: Is this option selected by default

    """

    label: str = attrs.field(repr=True, validator=str_validator)
    value: str = attrs.field(repr=True, validator=str_validator)
    description: Optional[str] = attrs.field(repr=True, default=None)
    emoji: Optional[Union["PartialEmoji", dict, str]] = attrs.field(
        repr=True, default=None, metadata=export_converter(process_emoji)
    )
    default: bool = attrs.field(repr=True, default=False)

    @classmethod
    def converter(cls, value: Any) -> "SelectOption":
        if isinstance(value, SelectOption):
            return value
        if isinstance(value, dict):
            return cls.from_dict(value)

        if isinstance(value, str):
            return cls(label=value, value=value)

        try:
            possible_iter = iter(value)

            return cls(label=possible_iter[0], value=possible_iter[1])
        except TypeError:
            pass

        raise TypeError(f"Cannot convert {value} of type {type(value)} to a SelectOption")

    @label.validator
    def _label_validator(self, attribute: str, value: str) -> None:
        if not value or len(value) > SELECT_MAX_NAME_LENGTH:
            raise ValueError("Label length should be between 1 and 100.")

    @value.validator
    def _value_validator(self, attribute: str, value: str) -> None:
        if not value or len(value) > SELECT_MAX_NAME_LENGTH:
            raise ValueError("Value length should be between 1 and 100.")

    @description.validator
    def _description_validator(self, attribute: str, value: str) -> None:
        if value is not None and len(value) > SELECT_MAX_NAME_LENGTH:
            raise ValueError("Description length must be 100 or lower.")


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class BaseSelectMenu(InteractiveComponent):
    """
    Represents a select menu component

    Attributes:
        custom_id str: A developer-defined identifier for the button, max 100 characters.
        placeholder str: The custom placeholder text to show if nothing is selected, max 100 characters.
        min_values Optional[int]: The minimum number of items that must be chosen. (default 1, min 0, max 25)
        max_values Optional[int]: The maximum number of items that can be chosen. (default 1, max 25)
        disabled bool: Disable the select and make it not intractable, default false.
        type Union[ComponentTypes, int]: The action role type number defined by discord. This cannot be modified.
    """

    min_values: int = attrs.field(repr=True, default=1, kw_only=True)
    max_values: int = attrs.field(repr=True, default=1, kw_only=True)
    placeholder: Optional[str] = attrs.field(repr=True, default=None, kw_only=True)

    # generic component attributes
    disabled: bool = attrs.field(repr=True, default=False, kw_only=True)
    custom_id: str = attrs.field(repr=True, factory=lambda: str(uuid.uuid4()), validator=str_validator, kw_only=True)
    type: Union[ComponentTypes, int] = attrs.field(
        repr=True, default=ComponentTypes.STRING_SELECT, init=False, on_setattr=attrs.setters.frozen
    )

    @placeholder.validator
    def _placeholder_validator(self, attribute: str, value: str) -> None:
        if value is not None and len(value) > SELECT_MAX_NAME_LENGTH:
            raise ValueError("Placeholder length must be 100 or lower.")

    @min_values.validator
    def _min_values_validator(self, attribute: str, value: int) -> None:
        if value < 0:
            raise ValueError("StringSelectMenu min value cannot be a negative number.")

    @max_values.validator
    def _max_values_validator(self, attribute: str, value: int) -> None:
        if value < 0:
            raise ValueError("StringSelectMenu max value cannot be a negative number.")

    def _check_object(self) -> None:
        super()._check_object()
        if not self.custom_id:
            raise TypeError("You need to have a custom id to identify the select.")

        if self.max_values < self.min_values:
            raise TypeError("Selects max value cannot be less than min value.")


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class StringSelectMenu(BaseSelectMenu):
    """
    Represents a string select component.

    Attributes:
        options List[dict]: The choices in the select, max 25.
        custom_id str: A developer-defined identifier for the button, max 100 characters.
        placeholder str: The custom placeholder text to show if nothing is selected, max 100 characters.
        min_values Optional[int]: The minimum number of items that must be chosen. (default 1, min 0, max 25)
        max_values Optional[int]: The maximum number of items that can be chosen. (default 1, max 25)
        disabled bool: Disable the select and make it not intractable, default false.
        type Union[ComponentTypes, int]: The action role type number defined by discord. This cannot be modified.
    """

    options: list[SelectOption | str] = attrs.field(repr=True, converter=list_converter(SelectOption.converter))
    type: Union[ComponentTypes, int] = attrs.field(
        repr=True, default=ComponentTypes.STRING_SELECT, init=False, on_setattr=attrs.setters.frozen
    )

    @options.validator
    def _options_validator(self, attribute: str, value: List[Union[SelectOption, Dict]]) -> None:
        if not all(isinstance(x, (SelectOption, Dict)) for x in value):
            raise ValueError("StringSelectMenu options must be of type `SelectOption`")

    def _check_object(self) -> None:
        super()._check_object()

        if not self.options:
            raise TypeError("Selects needs to have at least 1 option.")

        if len(self.options) > SELECTS_MAX_OPTIONS:
            raise TypeError("Selects can only hold 25 options")

    def add_option(self, option: str | SelectOption) -> None:
        option = SelectOption.converter(option)
        self.options.append(option)


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class UserSelectMenu(BaseSelectMenu):
    """
    Represents a user select component.

    Attributes:
        custom_id str: A developer-defined identifier for the button, max 100 characters.
        placeholder str: The custom placeholder text to show if nothing is selected, max 100 characters.
        min_values Optional[int]: The minimum number of items that must be chosen. (default 1, min 0, max 25)
        max_values Optional[int]: The maximum number of items that can be chosen. (default 1, max 25)
        disabled bool: Disable the select and make it not intractable, default false.
        type Union[ComponentTypes, int]: The action role type number defined by discord. This cannot be modified.
    """

    type: Union[ComponentTypes, int] = attrs.field(
        repr=True, default=ComponentTypes.USER_SELECT, init=False, on_setattr=attrs.setters.frozen
    )


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class RoleSelectMenu(BaseSelectMenu):
    """
    Represents a role select component.

    Attributes:
        custom_id str: A developer-defined identifier for the button, max 100 characters.
        placeholder str: The custom placeholder text to show if nothing is selected, max 100 characters.
        min_values Optional[int]: The minimum number of items that must be chosen. (default 1, min 0, max 25)
        max_values Optional[int]: The maximum number of items that can be chosen. (default 1, max 25)
        disabled bool: Disable the select and make it not intractable, default false.
        type Union[ComponentTypes, int]: The action role type number defined by discord. This cannot be modified.
    """

    type: Union[ComponentTypes, int] = attrs.field(
        repr=True, default=ComponentTypes.ROLE_SELECT, init=False, on_setattr=attrs.setters.frozen
    )


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class MentionableSelectMenu(BaseSelectMenu):
    """
    Represents a mentionable select component.

    Attributes:
        custom_id str: A developer-defined identifier for the button, max 100 characters.
        placeholder str: The custom placeholder text to show if nothing is selected, max 100 characters.
        min_values Optional[int]: The minimum number of items that must be chosen. (default 1, min 0, max 25)
        max_values Optional[int]: The maximum number of items that can be chosen. (default 1, max 25)
        disabled bool: Disable the select and make it not intractable, default false.
        type Union[ComponentTypes, int]: The action role type number defined by discord. This cannot be modified.
    """

    type: Union[ComponentTypes, int] = attrs.field(
        repr=True, default=ComponentTypes.MENTIONABLE_SELECT, init=False, on_setattr=attrs.setters.frozen
    )


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class ChannelSelectMenu(BaseSelectMenu):
    """
    Represents a channel select component.

    Attributes:
        channel_types List[ChannelTypes]: List of channel types to include in the selection
        custom_id str: A developer-defined identifier for the button, max 100 characters.
        placeholder str: The custom placeholder text to show if nothing is selected, max 100 characters.
        min_values Optional[int]: The minimum number of items that must be chosen. (default 1, min 0, max 25)
        max_values Optional[int]: The maximum number of items that can be chosen. (default 1, max 25)
        disabled bool: Disable the select and make it not intractable, default false.
        type Union[ComponentTypes, int]: The action role type number defined by discord. This cannot be modified.
    """

    channel_types: list[ChannelTypes] = attrs.field(factory=list, repr=True, converter=list_converter(ChannelTypes))

    type: Union[ComponentTypes, int] = attrs.field(
        repr=True, default=ComponentTypes.CHANNEL_SELECT, init=False, on_setattr=attrs.setters.frozen
    )


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class ActionRow(BaseComponent):
    """
    Represents an action row.

    Attributes:
        components List[Union[dict, StringSelectMenu, Button]]: The components within this action row
        type Union[ComponentTypes, int]: The action role type number defined by discord. This cannot be modified.

    """

    _max_items = ACTION_ROW_MAX_ITEMS

    components: Sequence[Union[dict, StringSelectMenu, Button]] = attrs.field(repr=True, factory=list)
    type: Union[ComponentTypes, int] = attrs.field(
        repr=False, default=ComponentTypes.ACTION_ROW, init=False, on_setattr=attrs.setters.frozen
    )

    def __init__(self, *components: Union[dict, StringSelectMenu, Button]) -> None:
        self.__attrs_init__(components)
        self.components = [self._component_checks(c) for c in self.components]

    def __len__(self) -> int:
        return len(self.components)

    @classmethod
    def from_dict(cls, data) -> "ActionRow":
        return cls(*data["components"])

    def _component_checks(self, component: Union[dict, StringSelectMenu, Button]) -> Union[StringSelectMenu, Button]:
        if isinstance(component, dict):
            component = BaseComponent.from_dict_factory(component)

        if not issubclass(type(component), InteractiveComponent):
            raise TypeError("You can only add select or button to the action row.")

        component._check_object()
        return component

    def _check_object(self) -> None:
        if not (0 < len(self.components) <= ActionRow._max_items):
            raise TypeError(f"Number of components in one row should be between 1 and {ActionRow._max_items}.")

        if any(x.type == ComponentTypes.STRING_SELECT for x in self.components) and len(self.components) != 1:
            raise TypeError("Action row must have only one select component and nothing else.")

    def add_components(self, *components: Union[dict, Button, StringSelectMenu]) -> None:
        """
        Add one or more component(s) to this action row.

        Args:
            *components: The components to add

        """
        self.components += [self._component_checks(c) for c in components]


def process_components(
    components: Optional[
        Union[List[List[Union[BaseComponent, Dict]]], List[Union[BaseComponent, Dict]], BaseComponent, Dict]
    ]
) -> List[Dict]:
    """
    Process the passed components into a format discord will understand.

    Args:
        components: List of dict / components to process

    Returns:
        formatted dictionary for discord

    Raises:
        ValueError: Invalid components

    """
    if not components:
        # Its just empty, so nothing to process.
        return components

    if isinstance(components, dict):
        # If a naked dictionary is passed, assume the user knows what they're doing and send it blindly
        # after wrapping it in a list for discord
        return [components]

    if issubclass(type(components), BaseComponent):
        # Naked component was passed
        components = [components]

    if isinstance(components, list):
        if all(isinstance(c, dict) for c in components):
            # user has passed a list of dicts, this is the correct format, blindly send it
            return components

        if all(isinstance(c, list) for c in components):
            # list of lists... actionRow-less sending
            return [ActionRow(*row).to_dict() for row in components]

        if all(issubclass(type(c), InteractiveComponent) for c in components):
            # list of naked components
            return [ActionRow(*components).to_dict()]

        if all(isinstance(c, ActionRow) for c in components):
            # we have a list of action rows
            return [action_row.to_dict() for action_row in components]

    raise ValueError(f"Invalid components: {components}")


def spread_to_rows(*components: Union[ActionRow, Button, StringSelectMenu], max_in_row: int = 5) -> List[ActionRow]:
    """
    A helper function that spreads your components into `ActionRow`s of a set size.

    Args:
        *components: The components to spread, use `None` to explicit start a new row
        max_in_row: The maximum number of components in each row

    Returns:
        List[ActionRow] of components spread to rows

    Raises:
        ValueError: Too many or few components or rows

    """
    # todo: incorrect format errors
    if not components or len(components) > 25:
        raise ValueError("Number of components should be between 1 and 25.")
    if not 1 <= max_in_row <= 5:
        raise ValueError("max_in_row should be between 1 and 5.")

    rows = []
    button_row = []
    for component in list(components):
        if component is not None and component.type == ComponentTypes.BUTTON:
            button_row.append(component)

            if len(button_row) == max_in_row:
                rows.append(ActionRow(*button_row))
                button_row = []

            continue

        if button_row:
            rows.append(ActionRow(*button_row))
            button_row = []

        if component is not None:
            if component.type == ComponentTypes.ACTION_ROW:
                rows.append(component)
            elif component.type == ComponentTypes.STRING_SELECT:
                rows.append(ActionRow(component))
    if button_row:
        rows.append(ActionRow(*button_row))

    if len(rows) > 5:
        raise ValueError("Number of rows exceeds 5.")

    return rows


def get_components_ids(component: Union[str, dict, list, InteractiveComponent]) -> Iterator[str]:
    """
    Creates a generator with the `custom_id` of a component or list of components.

    Args:
        component: Objects to get `custom_id`s from

    Returns:
        Generator with the `custom_id` of a component or list of components.

    Raises:
        ValueError: Unknown component type

    """
    if isinstance(component, str):
        yield component
    elif isinstance(component, dict):
        if component["type"] == ComponentTypes.actionrow:
            yield from (comp["custom_id"] for comp in component["components"] if "custom_id" in comp)
        elif "custom_id" in component:
            yield component["custom_id"]
    elif c_id := getattr(component, "custom_id", None):
        yield c_id
    elif isinstance(component, ActionRow):
        yield from (comp_id for comp in component.components for comp_id in get_components_ids(comp))

    elif isinstance(component, list):
        yield from (comp_id for comp in component for comp_id in get_components_ids(comp))
    else:
        raise ValueError(f"Unknown component type of {component} ({type(component)}). " f"Expected str, dict or list")


TYPE_ALL_COMPONENT = Union[ActionRow, Button, StringSelectMenu]

TYPE_COMPONENT_MAPPING = {
    ComponentTypes.ACTION_ROW: ActionRow,
    ComponentTypes.BUTTON: Button,
    ComponentTypes.STRING_SELECT: StringSelectMenu,
    ComponentTypes.USER_SELECT: UserSelectMenu,
    ComponentTypes.CHANNEL_SELECT: ChannelSelectMenu,
    ComponentTypes.ROLE_SELECT: RoleSelectMenu,
    ComponentTypes.MENTIONABLE_SELECT: MentionableSelectMenu,
}
