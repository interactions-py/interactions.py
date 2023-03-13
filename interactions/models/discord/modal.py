import uuid
from enum import IntEnum
from typing import Union, Optional, Any, TypeVar

import discord_typings

from interactions.client.const import MISSING
from interactions.client.mixins.serialization import DictSerializationMixin
from interactions.client.utils import dict_filter
from interactions.models.discord.components import ComponentType
from interactions.models.internal.application_commands import CallbackType

__all__ = ("InputText", "Modal", "ParagraphText", "ShortText", "TextStyles")

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
    def from_dict(cls, data: dict[str, Any]) -> T:
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


class Modal:
    def __init__(
        self,
        *components: InputText,
        title: str,
        custom_id: Optional[str] = None,
    ) -> None:
        self.title: str = title
        self.components: list[InputText] = list(components)
        self.custom_id: str = custom_id or str(uuid.uuid4())

        self.type = CallbackType.MODAL

    def to_dict(self) -> discord_typings.ModalInteractionData:
        return {
            "type": self.type,
            "data": {
                "title": self.title,
                "custom_id": self.custom_id,
                "components": [
                    {
                        "type": ComponentType.ACTION_ROW,
                        "components": [c.to_dict() if hasattr(c, "to_dict") else c],
                    }
                    for c in self.components
                ],
            },
        }

    def add_components(self, *components: InputText) -> None:
        """
        Add components to the modal.

        Args:
            *components: The components to add.
        """
        if len(components) == 1 and isinstance(components[0], (list, tuple)):
            components = components[0]
        self.components.extend(components)
