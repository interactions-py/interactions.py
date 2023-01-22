from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import attrs
from attrs.validators import instance_of
from attrs.validators import optional as v_optional

from interactions.client.const import (
    EMBED_MAX_NAME_LENGTH,
    EMBED_MAX_FIELDS,
    EMBED_MAX_DESC_LENGTH,
    EMBED_TOTAL_MAX,
    EMBED_FIELD_VALUE_LENGTH,
)
from interactions.client.mixins.serialization import DictSerializationMixin
from interactions.client.utils.attr_converters import optional as c_optional, list_converter
from interactions.client.utils.attr_converters import timestamp_converter
from interactions.client.utils.serializer import no_export_meta, export_converter
from interactions.models.discord.color import Color, process_color
from interactions.models.discord.enums import EmbedTypes
from interactions.models.discord.timestamp import Timestamp

__all__ = (
    "EmbedField",
    "EmbedAuthor",
    "EmbedAttachment",
    "EmbedAuthor",
    "EmbedFooter",
    "EmbedProvider",
    "Embed",
    "process_embeds",
)


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class EmbedField(DictSerializationMixin):
    """
    Representation of an embed field.

    Attributes:
        name: Field name
        value: Field value
        inline: If the field should be inline

    """

    name: str = attrs.field(
        repr=False,
    )
    value: str = attrs.field(
        repr=False,
    )
    inline: bool = attrs.field(repr=False, default=False)

    @name.validator
    def _name_validation(self, attribute: str, value: Any) -> None:
        if len(value) > EMBED_MAX_NAME_LENGTH:
            raise ValueError(f"Field name cannot exceed {EMBED_MAX_NAME_LENGTH} characters")

    @value.validator
    def _value_validation(self, attribute: str, value: Any) -> None:
        if len(value) > EMBED_FIELD_VALUE_LENGTH:
            raise ValueError(f"Field value cannot exceed {EMBED_FIELD_VALUE_LENGTH} characters")

    def __len__(self) -> int:
        return len(self.name) + len(self.value)


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class EmbedAuthor(DictSerializationMixin):
    """
    Representation of an embed author.

    Attributes:
        name: Name to show on embed
        url: Url to go to when name is clicked
        icon_url: Icon to show next to name
        proxy_icon_url: Proxy icon url

    """

    name: Optional[str] = attrs.field(repr=False, default=None)
    url: Optional[str] = attrs.field(repr=False, default=None)
    icon_url: Optional[str] = attrs.field(repr=False, default=None)
    proxy_icon_url: Optional[str] = attrs.field(repr=False, default=None, metadata=no_export_meta)

    @name.validator
    def _name_validation(self, attribute: str, value: Any) -> None:
        if len(value) > EMBED_MAX_NAME_LENGTH:
            raise ValueError(f"Field name cannot exceed {EMBED_MAX_NAME_LENGTH} characters")

    def __len__(self) -> int:
        return len(self.name)


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class EmbedAttachment(DictSerializationMixin):  # thumbnail or image or video
    """
    Representation of an attachment.

    Attributes:
        url: Attachment url
        proxy_url: Proxy url
        height: Attachment height
        width: Attachment width

    """

    url: Optional[str] = attrs.field(repr=False, default=None)
    proxy_url: Optional[str] = attrs.field(repr=False, default=None, metadata=no_export_meta)
    height: Optional[int] = attrs.field(repr=False, default=None, metadata=no_export_meta)
    width: Optional[int] = attrs.field(repr=False, default=None, metadata=no_export_meta)

    @classmethod
    def _process_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(data, str):
            return {"url": data}
        return data

    @property
    def size(self) -> tuple[Optional[int], Optional[int]]:
        return self.height, self.width


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class EmbedFooter(DictSerializationMixin):
    """
    Representation of an Embed Footer.

    Attributes:
        text: Footer text
        icon_url: Footer icon url
        proxy_icon_url: Proxy icon url

    """

    text: str = attrs.field(
        repr=False,
    )
    icon_url: Optional[str] = attrs.field(repr=False, default=None)
    proxy_icon_url: Optional[str] = attrs.field(repr=False, default=None, metadata=no_export_meta)

    @classmethod
    def converter(cls, ingest: Union[dict, str, "EmbedFooter"]) -> "EmbedFooter":
        """
        A converter to handle users passing raw strings or dictionaries as footers to the Embed object.

        Args:
            ingest: The data to convert

        Returns:
            An EmbedFooter object
        """
        if isinstance(ingest, str):
            return cls(text=ingest)
        else:
            return cls.from_dict(ingest)

    def __len__(self) -> int:
        return len(self.text)


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class EmbedProvider(DictSerializationMixin):
    """
    Represents an embed's provider.

    !!! note
        Only used by system embeds, not bots

    Attributes:
        name: Provider name
        url: Provider url

    """

    name: Optional[str] = attrs.field(repr=False, default=None)
    url: Optional[str] = attrs.field(repr=False, default=None)


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class Embed(DictSerializationMixin):
    """Represents a discord embed object."""

    title: Optional[str] = attrs.field(default=None, repr=True)
    """The title of the embed"""
    description: Optional[str] = attrs.field(default=None, repr=True)
    """The description of the embed"""
    color: Optional[Union[Color, dict, tuple, list, str, int]] = attrs.field(
        default=None, repr=True, metadata=export_converter(process_color)
    )
    """The colour of the embed"""
    url: Optional[str] = attrs.field(default=None, validator=v_optional(instance_of(str)), repr=True)
    """The url the embed should direct to when clicked"""
    timestamp: Optional[Timestamp] = attrs.field(
        default=None,
        converter=c_optional(timestamp_converter),
        validator=v_optional(instance_of((datetime, float, int))),
        repr=True,
    )
    """Timestamp of embed content"""
    fields: List[EmbedField] = attrs.field(factory=list, converter=EmbedField.from_list, repr=True)
    """A list of [fields][interactions.models.discord.embed.EmbedField] to go in the embed"""
    author: Optional[EmbedAuthor] = attrs.field(repr=False, default=None, converter=c_optional(EmbedAuthor.from_dict))
    """The author of the embed"""
    thumbnail: Optional[EmbedAttachment] = attrs.field(
        repr=False, default=None, converter=c_optional(EmbedAttachment.from_dict)
    )
    """The thumbnail of the embed"""
    images: list[EmbedAttachment] = attrs.field(
        repr=False, factory=list, converter=list_converter(EmbedAttachment.from_dict)
    )
    """The images of the embed"""
    video: Optional[EmbedAttachment] = attrs.field(
        repr=False,
        default=None,
        converter=c_optional(EmbedAttachment.from_dict),
        metadata=no_export_meta,
    )
    """The video of the embed, only used by system embeds"""
    footer: Optional[EmbedFooter] = attrs.field(repr=False, default=None, converter=c_optional(EmbedFooter.converter))
    """The footer of the embed"""
    provider: Optional[EmbedProvider] = attrs.field(
        repr=False,
        default=None,
        converter=c_optional(EmbedProvider.from_dict),
        metadata=no_export_meta,
    )
    """The provider of the embed, only used for system embeds"""
    type: EmbedTypes = attrs.field(
        repr=False,
        default=EmbedTypes.RICH,
        converter=c_optional(EmbedTypes),
        metadata=no_export_meta,
    )

    @title.validator
    def _name_validation(self, attribute: str, value: Any) -> None:
        """Validate the embed title."""
        if value is not None:
            if isinstance(value, str):
                if len(value) > EMBED_MAX_NAME_LENGTH:
                    raise ValueError(f"Title cannot exceed {EMBED_MAX_NAME_LENGTH} characters")
                return
            raise TypeError("Title must be of type String")

    @description.validator
    def _description_validation(self, attribute: str, value: Any) -> None:
        """Validate the description."""
        if value is not None:
            if isinstance(value, str):
                if len(value) > EMBED_MAX_DESC_LENGTH:
                    raise ValueError(f"Description cannot exceed {EMBED_MAX_DESC_LENGTH} characters")
                return
            raise TypeError("Description must be of type String")

    @fields.validator
    def _fields_validation(self, attribute: str, value: Any) -> None:
        """Validate the fields."""
        if isinstance(value, list):
            if len(value) > EMBED_MAX_FIELDS:
                raise ValueError(f"Embeds can only hold {EMBED_MAX_FIELDS} fields")

    def _check_object(self) -> None:
        self._name_validation("title", self.title)
        self._description_validation("description", self.description)
        self._fields_validation("fields", self.fields)

        if len(self) > EMBED_TOTAL_MAX:
            raise ValueError(
                "Your embed is too large, more info at https://discord.com/developers/docs/resources/channel#embed-limits"
            )

    def __len__(self) -> int:
        # yes i know there are far more optimal ways to write this
        # its written like this for readability
        total: int = 0
        if self.title:
            total += len(self.title)
        if self.description:
            total += len(self.description)
        if self.footer:
            total += len(self.footer)
        if self.author:
            total += len(self.author)
        if self.fields:
            total += sum(map(len, self.fields))
        return total

    def __bool__(self) -> bool:
        return any(
            (
                self.title,
                self.description,
                self.fields,
                self.author,
                self.thumbnail,
                self.footer,
                self.images,
                self.video,
            )
        )

    def set_author(
        self,
        name: str,
        url: Optional[str] = None,
        icon_url: Optional[str] = None,
    ) -> None:
        """
        Set the author field of the embed.

        Args:
            name: The text to go in the title section
            url: A url link to the author
            icon_url: A url of an image to use as the icon

        """
        self.author = EmbedAuthor(name=name, url=url, icon_url=icon_url)

    def set_thumbnail(self, url: str) -> None:
        """
        Set the thumbnail of the embed.

        Args:
            url: the url of the image to use

        """
        self.thumbnail = EmbedAttachment(url=url)

    def set_image(self, url: str) -> None:
        """
        Set the image of the embed.

        Args:
            url: the url of the image to use

        """
        self.images = [EmbedAttachment(url=url)]

    def set_images(self, *images: str) -> None:
        """
        Set multiple images for the embed.

        Note:
            To use multiple images, you must also set a url for this embed.

        Warning:
            This takes advantage of an undocumented feature of the API, and may be removed at any time.

        Args:
            images: the images to use

        """
        if len(self.images) + 1 > 1 and not self.url:
            raise ValueError("To use multiple images, you must also set a url for this embed")

        self.images = [EmbedAttachment(url=url) for url in images]

    def add_image(self, image: str) -> None:
        """
        Add an image to the embed.

        Note:
            To use multiple images, you must also set a url for this embed.

        Warning:
            This takes advantage of an undocumented feature of the API, and may be removed at any time.

        Args:
            image: the image to add
        """
        if len(self.images) + 1 > 1 and not self.url:
            raise ValueError("To use multiple images, you must also set a url for this embed")
        self.images.append(EmbedAttachment(url=image))

    def set_footer(self, text: str, icon_url: Optional[str] = None) -> None:
        """
        Set the footer field of the embed.

        Args:
            text: The text to go in the title section
            icon_url: A url of an image to use as the icon

        """
        self.footer = EmbedFooter(text=text, icon_url=icon_url)

    def add_field(self, name: str, value: Any, inline: bool = False) -> None:
        """
        Add a field to the embed.

        Args:
            name: The title of this field
            value: The value in this field
            inline: Should this field be inline with other fields?

        """
        self.fields.append(EmbedField(name, str(value), inline))
        self._fields_validation("fields", self.fields)

    def add_fields(self, *fields: EmbedField | str | dict) -> None:
        """
        Add multiple fields to the embed.

        Args:
            fields: The fields to add

        """
        for _field in fields:
            if isinstance(_field, EmbedField):
                self.fields.append(_field)
                self._fields_validation("fields", self.fields)
            elif isinstance(_field, str):
                self.add_field(_field, _field)
            elif isinstance(_field, dict):
                self.add_field(**_field)
            else:
                raise TypeError(f"Expected EmbedField, str or dict, got {type(_field).__name__}")

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        images = data.pop("images", [])

        if images:
            if len(images) > 1:
                if not self.url:
                    raise ValueError("To use multiple images, you must also set a url for this embed")

                data["image"] = images[0]
                data = [data]

                for image in images[1:]:
                    data.append({"image": image, "url": self.url})
            else:
                data["image"] = images[0]

        return data


def process_embeds(embeds: Optional[Union[List[Union[Embed, Dict]], Union[Embed, Dict]]]) -> Optional[List[dict]]:
    """
    Process the passed embeds into a format discord will understand.

    Args:
        embeds: List of dict / embeds to process

    Returns:
        formatted list for discord

    """
    if embeds is None:
        # Its just empty, so nothing to process.
        return embeds

    if isinstance(embeds, Embed):
        # Single embed, convert it to dict and wrap it into a list for discord.
        out = embeds.to_dict()
        if isinstance(out, list):
            return out
        return [out]

    if isinstance(embeds, dict):
        # We assume the dict correctly represents a single discord embed and just send it blindly
        # after wrapping it in a list for discord
        return [embeds]

    if isinstance(embeds, list):
        # A list of embeds, convert Embed to dict representation if needed.
        out = [embed.to_dict() if isinstance(embed, Embed) else embed for embed in embeds]
        if any(isinstance(embed, list) for embed in out):
            raise ValueError("You cannot send multiple embeds when using multiple images in a single embed")
        return out

    raise ValueError(f"Invalid embeds: {embeds}")
