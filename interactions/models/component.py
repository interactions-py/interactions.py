from typing import List, Optional

from ..api.error import InteractionException
from ..api.models.message import Emoji
from ..api.models.misc import DictSerializerMixin
from ..enums import ButtonStyle, ComponentType, TextStyleType


class SelectOption(DictSerializerMixin):
    """
    A class object representing the select option of a select menu.

    The structure for a select option:

    .. code-block:: python

        interactions.SelectOption(
            label="I'm a cool option. :)",
            value="internal_option_value",
            description="some extra info about me! :D",
        )

    :ivar str label: The label of the select option.
    :ivar str value: The returned value of the select option.
    :ivar Optional[str] description?: The description of the select option.
    :ivar Optional[Emoji] emoji?: The emoji used alongside the label of the select option.
    :ivar Optional[bool] default?: Whether the select option is the default for the select menu.
    """

    __slots__ = ("_json", "label", "value", "description", "emoji", "default")
    label: str
    value: str
    description: Optional[str]
    emoji: Optional[Emoji]
    default: Optional[bool]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.emoji = (
            Emoji(**self.emoji if isinstance(self.emoji, dict) else self.emoji._json)
            if self._json.get("emoji")
            else None
        )
        if self.emoji:
            self._json.update({"emoji": self.emoji._json})


class SelectMenu(DictSerializerMixin):
    """
    A class object representing the select menu of a component.

    The structure for a select menu:

    .. code-block:: python

        interactions.SelectMenu(
            options=[interactions.SelectOption(...)],
            placeholder="Check out my options. :)",
            custom_id="menu_component",
        )

    :ivar ComponentType type: The type of select menu. Always defaults to ``3``.
    :ivar str custom_id: The customized "ID" of the select menu.
    :ivar List[SelectOption] options: The list of select options in the select menu.
    :ivar Optional[str] placeholder?: The placeholder of the select menu.
    :ivar Optional[int] min_values?: The minimum "options"/values to choose from the component.
    :ivar Optional[int] max_values?: The maximum "options"/values to choose from the component.
    :ivar Optional[bool] disabled?: Whether the select menu is unable to be used.
    """

    __slots__ = (
        "_json",
        "type",
        "custom_id",
        "options",
        "placeholder",
        "min_values",
        "max_values",
        "disabled",
        "label",
        "value",
    )
    type: ComponentType
    custom_id: str
    options: List[SelectOption]
    placeholder: Optional[str]
    min_values: Optional[int]
    max_values: Optional[int]
    disabled: Optional[bool]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.type = ComponentType.SELECT
        self.options = (
            [
                option if isinstance(option, SelectOption) else SelectOption(**option)
                for option in self.options
            ]
            if self._json.get("options")
            else None
        )
        self._json.update({"type": self.type.value})
        self._json.update({"options": [option._json for option in self.options]})


class Button(DictSerializerMixin):
    """
    A class object representing the button of a component.

    The structure for a button:

    .. code-block:: python

        interactions.Button(
            style=interactions.ButtonStyle.DANGER,
            label="Delete",
            custom_id="delete_message",
        )

    :ivar ComponentType type: The type of button. Always defaults to ``2``.
    :ivar ButtonStyle style: The style of the button.
    :ivar str label: The label of the button.
    :ivar Optional[Emoji] emoji?: The emoji used alongside the label of the button.
    :ivar Optional[str] custom_id?: The customized "ID" of the button.
    :ivar Optional[str] url?: The URL route/path of the button.
    :ivar Optional[bool] disabled?: Whether the button is unable to be used.
    """

    __slots__ = ("_json", "type", "style", "label", "emoji", "custom_id", "url", "disabled")
    type: ComponentType
    style: ButtonStyle
    label: str
    emoji: Optional[Emoji]
    custom_id: Optional[str]
    url: Optional[str]
    disabled: Optional[bool]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.type = ComponentType.BUTTON
        self.style = ButtonStyle(self.style)
        self._json.update({"type": self.type.value, "style": self.style.value})


class Component(DictSerializerMixin):
    """
    A class object representing the component in an interaction response/followup.

    .. note::
        ``components`` is only applicable if an ActionRow is supported, otherwise
        ActionRow-less will be opted. ``list`` is in reference to the class.

    .. warning::
        This object object class is only inferred upon when the gateway is processing
        back information involving a component. Do not use this object for sending.

    :ivar ComponentType type: The type of component.
    :ivar Optional[str] custom_id?: The customized "ID" of the component.
    :ivar Optional[bool] disabled?: Whether the component is unable to be used.
    :ivar Optional[ButtonStyle] style?: The style of the component.
    :ivar Optional[str] label?: The label of the component.
    :ivar Optional[Emoji] emoji?: The emoji used alongside the label of the component.
    :ivar Optional[str] url?: The URl route/path of the component.
    :ivar Optional[List[SelectMenu]] options?: The "choices"/options of the component.
    :ivar Optional[str] placeholder?: The placeholder text/value of the component.
    :ivar Optional[int] min_values?: The minimum "options"/values to choose from the component.
    :ivar Optional[int] max_values?: The maximum "options"/values to choose from the component.
    :ivar Optional[List[Component]] components?: A list of components nested in the component.
    :ivar Optional[int] min_length?: The minimum input length to choose from the component.
    :ivar Optional[int] max_length?: The maximum input length to choose from the component.
    :ivar Optional[bool] required?: Whether this component is required to be filled.
    :ivar Optional[str] value?: The pre-filled value of the component.
    """

    __slots__ = (
        "_json",
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
        "min_length",
        "max_length",
        "required",
        "value",
    )
    type: ComponentType
    custom_id: Optional[str]
    disabled: Optional[bool]
    style: Optional[ButtonStyle]
    label: Optional[str]
    emoji: Optional[Emoji]
    url: Optional[str]
    options: Optional[List[SelectMenu]]
    placeholder: Optional[str]
    min_values: Optional[int]
    max_values: Optional[int]
    components: Optional[List["Component"]]
    min_length: Optional[int]
    max_length: Optional[int]
    required: Optional[bool]
    value: Optional[str]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.type = ComponentType(self.type)
        self.style = ButtonStyle(self.style) if self._json.get("style") else None
        self.options = (
            [
                SelectOption(**option._json)
                if isinstance(option, SelectOption)
                else SelectOption(**option)
                for option in self.options
            ]
            if self._json.get("options")
            else None
        )
        if self._json.get("components"):
            self._json["components"] = [component._json for component in self.components]


class TextInput(DictSerializerMixin):
    """
    A class object representing the text input of a modal.

    The structure for a text input:

    .. code-block:: python

        interactions.TextInput(
            style=interactions.TextStyleType.SHORT,
            label="Let's get straight to it: what's 1 + 1?",
            custom_id="text_input_response",
            min_length=2,
            max_length=3,
        )

    :ivar ComponentType type: The type of input. Always defaults to ``4``.
    :ivar TextStyleType style: The style of the input.
    :ivar str custom_id: The custom Id of the input.
    :ivar str label: The label of the input.
    :ivar Optional[str] value: The pre-filled value of the input.
    :ivar Optional[bool] required?: Whether the input is required or not.
    :ivar Optional[str] placeholder?: The placeholder of the input.
    :ivar Optional[int] min_length?: The minimum length of the input.
    :ivar Optional[int] max_length?: The maximum length of the input.
    """

    __slots__ = (
        "_json",
        "type",
        "style",
        "custom_id",
        "label",
        "value",
        "required",
        "placeholder",
        "min_length",
        "max_length",
    )
    type: ComponentType
    style: TextStyleType
    custom_id: str
    label: str
    value: Optional[str]
    required: Optional[bool]
    placeholder: Optional[str]
    min_length: Optional[int]
    max_length: Optional[int]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = ComponentType.INPUT_TEXT
        self.style = TextStyleType(self.style)
        self._json.update({"type": self.type.value, "style": self.style.value})


class Modal(DictSerializerMixin):
    """
    A class object representing a modal.

    The structure for a modal:

    .. code-block:: python

        interactions.Modal(
            title="Application Form",
            custom_id="mod_app_form",
            components=[interactions.TextInput(...)],
        )

    :ivar str custom_id: The custom ID of the modal.
    :ivar str title: The title of the modal.
    :ivar List[Component] components: The components of the modal.
    """

    __slots__ = ("_json", "custom_id", "title", "components")
    custom_id: str
    title: str
    components: List[Component]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.components = (
            [Component(**component._json) for component in self.components]
            if self._json.get("components")
            else None
        )
        self._json.update(
            {
                "components": [
                    {"type": 1, "components": [component._json]} for component in self.components
                ]
            }
        )


class ActionRow(DictSerializerMixin):
    """
    A class object representing the action row for interaction responses holding components.

    .. note::
        A message cannot have more than 5 ActionRow's supported.
        An ActionRow may also support only 1 text input component
        only.

    The structure for an action row:

    .. code-block:: python

        # "..." represents a component object.
        # Method 1:
        interactions.ActionRow(...)

        # Method 2:
        interactions.ActionRow(components=[...])

    :ivar int type: The type of component. Always defaults to ``1``.
    :ivar Optional[List[Component]] components?: A list of components the ActionRow has, if any.
    """

    __slots__ = ("_json", "type", "components")
    type: int
    components: Optional[List[Component]]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.type = ComponentType.ACTION_ROW
        for component in self.components:
            if isinstance(component, SelectMenu):
                component._json["options"] = [
                    option._json if isinstance(option, SelectOption) else option
                    for option in component._json["options"]
                ]
        self.components = (
            [Component(**component._json) for component in self.components]
            if self._json.get("components")
            else None
        )
        self._json.update({"type": self.type.value})
        if self._json.get("components"):
            self._json["components"] = [component._json for component in self.components]


def _build_components(components) -> List[dict]:
    def __check_action_row():

        if isinstance(components, list) and all(
            isinstance(action_row, (list, ActionRow)) for action_row in components
        ):
            _components = []
            for action_row in components:
                for component in (
                    action_row if isinstance(action_row, list) else action_row.components
                ):
                    if isinstance(component, SelectMenu):
                        component._json["options"] = [
                            option._json if not isinstance(option, dict) else option
                            for option in component.options
                        ]
                _components.append(
                    {
                        "type": 1,
                        "components": [
                            (
                                component._json
                                if component._json.get("custom_id") or component._json.get("url")
                                else []
                            )
                            for component in (
                                action_row
                                if isinstance(action_row, list)
                                else action_row.components
                            )
                        ],
                    }
                )
            return _components

        elif isinstance(components, ActionRow):
            _components: List[dict] = [{"type": 1, "components": []}]
            _components[0]["components"] = [
                (
                    component._json
                    if component._json.get("custom_id") or component._json.get("url")
                    else []
                )
                for component in components.components
            ]
            return _components
        else:
            return False

    def __check_components():
        if isinstance(components, list) and all(
            isinstance(component, (Button, SelectMenu)) for component in components
        ):
            for component in components:
                if isinstance(component, SelectMenu):
                    component._json["options"] = [
                        options._json if not isinstance(options, dict) else options
                        for options in component._json["options"]
                    ]
            _components = [
                {
                    "type": 1,
                    "components": [
                        (
                            component._json
                            if component._json.get("custom_id") or component._json.get("url")
                            else []
                        )
                        for component in components
                    ],
                }
            ]
            return _components

        elif isinstance(components, Button):
            _components: List[dict] = [{"type": 1, "components": []}]
            _components[0]["components"] = (
                [components._json]
                if components._json.get("custom_id") or components._json.get("url")
                else []
            )
            return _components
        elif isinstance(components, SelectMenu):
            _components: List[dict] = [{"type": 1, "components": []}]
            components._json["options"] = [
                options._json if not isinstance(options, dict) else options
                for options in components._json["options"]
            ]
            _components[0]["components"] = (
                [components._json]
                if components._json.get("custom_id") or components._json.get("url")
                else []
            )
            return _components
        else:
            raise InteractionException(
                11, message="The specified components are invalid and could not be created!"
            )

    _components = __check_action_row()

    if _components:
        return _components
    else:
        return __check_components()
