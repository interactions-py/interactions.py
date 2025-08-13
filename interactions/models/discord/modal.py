import uuid
from enum import IntEnum
from typing import Union, Optional, Any, TypeVar
from typing_extensions import Self

import discord_typings

from interactions.client.const import MISSING
from interactions.client.mixins.serialization import DictSerializationMixin
from interactions.client.utils import dict_filter, dict_filter_none
from interactions.models.discord.components import ComponentType, BaseComponent, StringSelectMenu
from interactions.models.internal.application_commands import CallbackType

__all__ = ("InputText", "Modal", "ParagraphText", "ShortText", "TextStyles", "LabelComponent")

T = TypeVar("T", bound="InputText")


class TextStyles(IntEnum):
    SHORT = 1
    PARAGRAPH = 2


class InputText(DictSerializationMixin):
    def __init__(
        self,
        *,
        label: str,
        style: Union[TextStyles, int],
        custom_id: Optional[str] = MISSING,
        placeholder: Optional[str] = MISSING,
        value: Optional[str] = MISSING,
        required: bool = True,
        min_length: Optional[int] = MISSING,
        max_length: Optional[int] = MISSING,
    ) -> None:
        self.label = label
        self.style = style
        self.custom_id = custom_id or str(uuid.uuid4())
        self.placeholder = placeholder
        self.value = value
        self.required = required
        self.min_length = min_length
        self.max_length = max_length

        self.type = ComponentType.INPUT_TEXT

    def to_dict(
        self,
    ) -> dict[str, int | str | bool]:  # I couldn't find a discord_typings object for this
        return dict_filter(
            {
                "type": self.type,
                "label": self.label,
                "style": self.style,
                "custom_id": self.custom_id,
                "placeholder": self.placeholder,
                "value": self.value,
                "required": self.required,
                "min_length": self.min_length,
                "max_length": self.max_length,
            }
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        if data["style"] == TextStyles.SHORT:
            cls = ShortText
        elif data["style"] == TextStyles.PARAGRAPH:
            cls = ParagraphText

        return cls(
            label=data["label"],
            custom_id=data["custom_id"],
            placeholder=data["placeholder"],
            value=data["value"],
            required=data["required"],
            min_length=data["min_length"],
            max_length=data["max_length"],
        )


class ShortText(InputText):
    def __init__(
        self,
        *,
        label: str,
        custom_id: Optional[str] = MISSING,
        placeholder: Optional[str] = MISSING,
        value: Optional[str] = MISSING,
        required: bool = True,
        min_length: Optional[int] = MISSING,
        max_length: Optional[int] = MISSING,
    ) -> None:
        super().__init__(
            style=TextStyles.SHORT,
            label=label,
            custom_id=custom_id,
            placeholder=placeholder,
            value=value,
            required=required,
            min_length=min_length,
            max_length=max_length,
        )


class ParagraphText(InputText):
    def __init__(
        self,
        *,
        label: str,
        custom_id: Optional[str] = MISSING,
        placeholder: Optional[str] = MISSING,
        value: Optional[str] = MISSING,
        required: bool = True,
        min_length: Optional[int] = MISSING,
        max_length: Optional[int] = MISSING,
    ) -> None:
        super().__init__(
            style=TextStyles.PARAGRAPH,
            label=label,
            custom_id=custom_id,
            placeholder=placeholder,
            value=value,
            required=required,
            min_length=min_length,
            max_length=max_length,
        )


class LabelComponent(BaseComponent):
    def __init__(
        self,
        *,
        label: str,
        description: Optional[str] = None,
        component: StringSelectMenu | InputText,
    ):
        self.label = label
        self.component = component
        self.description = description
        self.type = ComponentType.LABEL

    def to_dict(self) -> dict:
        return dict_filter_none(
            {
                "type": self.type,
                "label": self.label,
                "description": self.description,
                "component": self.component.to_dict() if hasattr(self.component, "to_dict") else self.component,
            }
        )

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            label=data["label"],
            description=data.get("description"),
            component=BaseComponent.from_dict_factory(
                data["component"],
                alternate_mapping={
                    ComponentType.INPUT_TEXT: InputText,
                    ComponentType.STRING_SELECT: StringSelectMenu,
                },
            ),
        )


class Modal:
    def __init__(
        self,
        *components: InputText | LabelComponent,
        title: str,
        custom_id: Optional[str] = None,
    ) -> None:
        self.title: str = title
        self.components: list[InputText | LabelComponent] = list(components)
        self.custom_id: str = custom_id or str(uuid.uuid4())

        self.type = CallbackType.MODAL

    def to_dict(self) -> discord_typings.ModalInteractionData:
        dict_components: list[dict] = []

        for component in self.components:
            if isinstance(component, InputText):
                dict_components.append({"type": ComponentType.ACTION_ROW, "components": [component.to_dict()]})
            elif isinstance(component, LabelComponent):
                dict_components.append(component.to_dict())
            else:
                # backwards compatibility behavior, remove in v6
                dict_components.append(
                    {
                        "type": ComponentType.ACTION_ROW,
                        "components": [component],
                    }
                )

        return {
            "type": self.type,
            "data": {
                "title": self.title,
                "custom_id": self.custom_id,
                "components": dict_components,
            },
        }

    def add_components(self, *components: InputText | LabelComponent) -> None:
        """
        Add components to the modal.

        Args:
            *components: The components to add.

        """
        if len(components) == 1 and isinstance(components[0], (list, tuple)):
            components = components[0]
        self.components.extend(components)
