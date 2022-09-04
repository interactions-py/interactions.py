import contextlib
from typing import List, Optional, Union

from ...api.error import LibraryException
from ...api.models.emoji import Emoji
from ...utils.attrs_utils import DictSerializerMixin, convert_list, define, field
from ...utils.missing import MISSING
from ..enums import ButtonStyle, ComponentType, TextStyleType

__all__ = (
    "SelectOption",
    "SelectMenu",
    "Button",
    "Component",
    "TextInput",
    "Modal",
    "ActionRow",
    "_build_components",
)


@define()
class ComponentMixin(DictSerializerMixin):
    """
    A mixin designed to let subclasses attribute changes be mirrored to their _json
    Arguably, this should be moved to the DictSerializerMixin, but testing would need to be done first
    """

    def __setattr__(self, key, value) -> None:
        super().__setattr__(key, value)
        if key not in {"_json", "_extras"} and (
            key not in self._json or value != self._json.get(key)
        ):
            if value is not None and value is not MISSING:
                with contextlib.suppress(AttributeError):
                    value = [val._json for val in value] if isinstance(value, list) else value._json
                self._json.update({key: value})
            elif value is None and key in self._json.keys():
                del self._json[key]


@define()
class SelectOption(ComponentMixin):
    """
    A class object representing the select option of a select menu.
    The structure for a select option: ::
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

    label: str = field()
    value: str = field()
    description: Optional[str] = field(default=None)
    emoji: Optional[Emoji] = field(converter=Emoji, default=None)
    default: Optional[bool] = field(default=None)

    def __attrs_post_init__(self):
        if self.emoji:
            self._json.update({"emoji": self.emoji._json})


@define()
class SelectMenu(ComponentMixin):
    """
    A class object representing the select menu of a component.
    The structure for a select menu: ::
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

    type: ComponentType = field(converter=ComponentType, default=ComponentType.SELECT)
    custom_id: str = field()
    options: List[SelectOption] = field(converter=convert_list(SelectOption))
    placeholder: Optional[str] = field(default=None)
    min_values: Optional[int] = field(default=None)
    max_values: Optional[int] = field(default=None)
    disabled: Optional[bool] = field(default=None)

    def __attrs_post_init__(self) -> None:
        self._json.update({"type": self.type.value})
        self._json.update({"options": [option._json for option in self.options]})


@define()
class Button(ComponentMixin):
    """
    A class object representing the button of a component.
    The structure for a button: ::
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

    type: ComponentType = field(converter=ComponentType, default=ComponentType.BUTTON)
    style: ButtonStyle = field(converter=ButtonStyle)
    label: str = field()
    emoji: Optional[Emoji] = field(converter=Emoji, default=None)
    custom_id: Optional[str] = field(default=None)
    url: Optional[str] = field(default=None)
    disabled: Optional[bool] = field(default=None)

    def __attrs_post_init__(self) -> None:
        self._json.update({"type": self.type.value, "style": self.style.value})
        if self.emoji:
            self._json.update({"emoji": self.emoji._json})


@define()
class Component(ComponentMixin):
    """
    A class object representing the component in an interaction response/followup.

    .. note::
        ``components`` is only applicable if an ActionRow is supported, otherwise
        ActionRow-less will be opted. ``list`` is in reference to the class.
    .. warning::
        This object class is only inferred upon when the gateway is processing
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

    type: ComponentType = field(converter=ComponentType)
    custom_id: Optional[str] = field(default=None)
    disabled: Optional[bool] = field(default=None)
    style: Optional[ButtonStyle] = field(converter=ButtonStyle, default=None)
    label: Optional[str] = field(default=None)
    emoji: Optional[Emoji] = field(converter=Emoji, default=None)
    url: Optional[str] = field(default=None)
    options: Optional[List[SelectOption]] = field(
        converter=convert_list(SelectOption), default=None
    )
    placeholder: Optional[str] = field(default=None)
    min_values: Optional[int] = field(default=None)
    max_values: Optional[int] = field(default=None)
    components: Optional[List["Component"]] = field(default=None)
    min_length: Optional[int] = field(default=None)
    max_length: Optional[int] = field(default=None)
    required: Optional[bool] = field(default=None)
    value: Optional[str] = field(default=None)

    def __attrs_post_init__(self):
        self.components = (
            [Component(**components) for components in self.components] if self.components else None
        )
        if self._json.get("components"):
            self._json["components"] = [component._json for component in self.components]


@define()
class TextInput(ComponentMixin):
    """
    A class object representing the text input of a modal.
    The structure for a text input: ::
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

    type: ComponentType = field(converter=ComponentType, default=ComponentType.INPUT_TEXT)
    style: TextStyleType = field(converter=TextStyleType)
    custom_id: str = field()
    label: str = field()
    value: Optional[str] = field(default=None)
    required: Optional[bool] = field(default=None)
    placeholder: Optional[str] = field(default=None)
    min_length: Optional[int] = field(default=None)
    max_length: Optional[int] = field(default=None)

    def __attrs_post_init__(self):
        self._json.update({"type": self.type.value, "style": self.style.value})


@define()
class Modal(ComponentMixin):
    """
    A class object representing a modal.
    The structure for a modal: ::
        interactions.Modal(
            title="Application Form",
            custom_id="mod_app_form",
            components=[interactions.TextInput(...)],
        )

    :ivar str custom_id: The custom ID of the modal.
    :ivar str title: The title of the modal.
    :ivar List[Component] components: The components of the modal.
    """

    custom_id: str = field()
    title: str = field()
    components: List[Component] = field(converter=convert_list(Component))

    def __attrs_post_init__(self):
        self._json.update(
            {
                "components": [
                    {"type": 1, "components": [component._json]} for component in self.components
                ]
            }
        )


@define()
class ActionRow(ComponentMixin):
    """
    A class object representing the action row for interaction responses holding components.

    .. note::
        A message cannot have more than 5 ActionRow's supported.
        An ActionRow may also support only 1 text input component
        only.

    The structure for an action row:
    ..code-block:: python
        # "..." represents a component object.
        # Method 1:
        interactions.ActionRow(...)
        # Method 2:
        interactions.ActionRow(components=[...])

    :ivar int type: The type of component. Always defaults to ``1``.
    :ivar Optional[List[Component]] components?: A list of components the ActionRow has, if any.
    """

    type: ComponentType = field(ComponentType, default=ComponentType.ACTION_ROW)
    components: Optional[List[Component]] = field(converter=convert_list(Component), default=None)

    def __attrs_post_init__(self) -> None:
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

    @classmethod
    def new(cls, *components: Union[Button, SelectMenu, TextInput]) -> "ActionRow":
        r"""
        A class method for creating a new ``ActionRow``.

        :param \*components: The components to add to the ``ActionRow``.
        :type \*components: Union[Button, SelectMenu, TextInput]
        :return: A new ``ActionRow``.
        :rtype: ActionRow
        """
        return cls(components=list(components))


def _build_components(components) -> List[dict]:
    # sourcery no-metrics
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
                            option if isinstance(option, dict) else option._json
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
                        options if isinstance(options, dict) else options._json
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
                options if isinstance(options, dict) else options._json
                for options in components._json["options"]
            ]

            _components[0]["components"] = (
                [components._json]
                if components._json.get("custom_id") or components._json.get("url")
                else []
            )
            return _components
        else:
            raise LibraryException(
                11, message="The specified components are invalid and could not be created!"
            )

    if not components:
        return components

    _components = __check_action_row()

    if _components:
        return _components
    else:
        return __check_components()
