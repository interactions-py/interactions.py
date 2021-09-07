from collections import OrderedDict
from typing import List, Optional, Union

from orjson import dumps

from ..api.models.message import Emoji
from ..enums import ButtonType, ComponentType


class SelectOption(object):
    """
    A class object representing the select option of a select menu.

    :ivar str label: The label of the select option.
    :ivar str value: The returned value of the select option.
    :ivar typing.Optional[str] description: The description of the select option.
    :ivar typing.Optional[interactions.api.models.message.Emoji] emoji: The emoji used alongside the label of the select option.
    :ivar typing.Optional[bool] default: Whether the select option is the default for the select menu.
    """

    __slots__ = ("label", "value", "description", "emoji", "default")
    label: str
    value: str
    description: Optional[str]
    emoji: Optional[Emoji]
    default: Optional[bool]


class SelectMenu(object):
    """
    A class object representing the select menu of a component.

    :ivar interactions.enums.ComponentType type: The type of select menu.
    :ivar str custom_id: The customized "ID" of the select menu.
    :ivar typing.List[interactions.models.component.SelectOption] options: The list of select options in the select menu.
    :ivar typing.Optional[str] placeholder: The placeholder of the select menu.
    :ivar typing.Optional[int] min_values: The minimum "options"/values to choose from the component.
    :ivar typing.Optional[int] max_values: The maximum "options"/values to choose from the component.
    :ivar typing.Optional[bool] disabled: Whether the select menu is unable to be used.
    """

    __slots__ = ("type", "custom_id", "placeholder", "min_values", "max_values", "disabled")
    type: ComponentType
    custom_id: str
    options: List[SelectOption]
    placeholder: Optional[str]
    min_values: Optional[int]
    max_values: Optional[int]
    disabled: Optional[bool]

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __new__(cls):
        comb = OrderedDict()

        for key, value in cls.__dict__:
            if value is not None:
                comb.update({key: value})

        return dumps(comb)


class ActionRow(object):
    ...


class Button(object):
    """
    A class object representing the button of a component.

    :ivar interactions.enums.ButtonType type: The type of button.
    :ivar interactions.enums.ButtonType style: The style of the button.
    :ivar str label: The label of the button.
    :ivar typing.Optional[interactions.api.models.message.Emoji] emoji: The emoji used alongside the laebl of the button.
    :ivar typing.Optional[str] custom_id: The customized "ID" of the button.
    :ivar typing.Optional[str] url: The URL route/path of the button.
    :ivar typing.Optional[bool] disabled: Whether the button is unable to be used.
    """

    __slots__ = ("type", "style", "label", "emoji", "custom_id", "url", "disabled")
    type: ButtonType
    style: ButtonType
    label: str
    emoji: Optional[Emoji]
    custom_id: Optional[str]
    url: Optional[str]
    disabled: Optional[bool]

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __new__(cls):
        comb = OrderedDict()

        for key, value in cls.__dict__:
            if value is not None:
                comb.update({key: value})

        return dumps(comb)


class Component(object):
    """
    A class object representing the componeent in an interaction response/followup.

    .. note::
        ``components`` is only applicable if an ActionRow is supported, otherwise
        ActionRow-less will be opted. ``list`` is in reference to the class.

    :ivar typing.Union[interactions.models.ActionRow, interactions.models.Button, interactions.models.Menu] type: The type of component.
    :ivar typing.Optional[str] custom_id: The customized "ID" of the component.
    :ivar typing.Optional[bool] disabled: Whether the component is unable to be used.
    :ivar typing.Optional[interactions.enums.ButtonType] style: The style of the component.
    :ivar typing.Optional[str] label: The label of the component.
    :ivar typing.Optional[interactions.api.models.message.Emoji] emoji: The emoji used alongside the label of the component.
    :ivar typing.Optional[str] url: The URl route/path of the component.
    :ivar typing.Optional[typing.List[interactions.models.Menu]] options: The "choices"/options of the component.
    :ivar typing.Optional[str] placeholder: The placeholder text/value of the component.
    :ivar typing.Optional[int] min_values: The minimum "options"/values to choose from the component.
    :ivar typing.Optional[int] max_values: The maximum "options"/values to choose from the component.
    :ivar typing.Optional[typing.Union[list, interactions.models.ActionRow, typing.List[interactions.models.ActionRow]]] components: A list of components nested in the component.
    """

    __slots__ = (
        "type",
        "custom_id",
        "disabled",
        "style",
        "label",
        "emoji",
        "url",
        "options",
        "placeholder",
        "min_values",
        "max_values",
        "components",
    )
    type: Union[ActionRow, ButtonType, SelectMenu]
    custom_id: Optional[str]
    disabled: Optional[bool]
    style: Optional[ButtonType]
    label: Optional[str]
    emoji: Optional[Emoji]
    url: Optional[str]
    options: Optional[List[SelectMenu]]
    placeholder: Optional[str]
    min_values: Optional[int]
    max_values: Optional[int]
    components: Optional[Union[list, ActionRow, List[ActionRow]]]
