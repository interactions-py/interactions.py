from functools import cached_property

import attrs

from interactions.client import const

__all__ = ("LocalisedField", "LocalizedField")


@attrs.define(eq=False, order=False, hash=False, slots=False)
class LocalisedField:
    """
    An object that enables support for localising fields.

    Supported locales: https://discord.com/developers/docs/reference#locales
    """

    default_locale: str = attrs.field(repr=False, default=const.default_locale)

    bulgarian: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "bg"})
    chinese_china: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "zh-CN"})
    chinese_taiwan: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "zh-TW"})
    croatian: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "hr"})
    czech: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "cs"})
    danish: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "da"})
    dutch: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "nl"})
    english_uk: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "en-GB"})
    english_us: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "en-US"})
    finnish: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "fi"})
    french: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "fr"})
    german: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "de"})
    greek: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "el"})
    hindi: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "hi"})
    hungarian: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "hu"})
    italian: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "it"})
    japanese: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "ja"})
    korean: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "ko"})
    lithuanian: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "lt"})
    norwegian: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "no"})
    polish: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "pl"})
    portuguese_brazilian: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "pt-BR"})
    romanian_romania: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "ro"})
    russian: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "ru"})
    spanish: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "es-ES"})
    swedish: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "sv-SE"})
    thai: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "th"})
    turkish: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "tr"})
    ukrainian: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "uk"})
    vietnamese: str | None = attrs.field(repr=False, default=None, metadata={"locale-code": "vi"})

    def __str__(self) -> str:
        return str(self.default)

    def __bool__(self) -> bool:
        return self.default is not None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: default_locale={self.default_locale}, value='{self}'>"

    @cached_property
    def _code_mapping(self) -> dict:
        """Generates a lookup table for this object on demand to allow for value retrieval with locale codes"""
        data = []
        for attr in self.__attrs_attrs__:
            if attr.name != self.default_locale:
                if code := attr.metadata.get("locale-code"):
                    data.append((code, attr.name))
        return dict(data)

    @property
    def default(self) -> str:
        """The default value based on the CONST default_locale"""
        return getattr(self, self.default_locale)

    def get_locale(self, locale: str) -> str:
        """
        Get the value for the specified locale. Supports locale-codes and locale names.

        Args:
            locale: The locale to fetch

        Returns:
            The localised string, or the default value
        """
        if val := getattr(self, locale, None):
            # Attempt to retrieve an attribute with the specified locale
            return val
        if attr := self._code_mapping.get(locale):
            # assume the locale is a code, and attempt to find an attribute with that code
            if val := getattr(self, attr, None):
                # if the value isn't None, return
                return val

        # no value was found, return default
        return self.default

    @classmethod
    def converter(cls, value: str | None) -> "LocalisedField":
        if isinstance(value, LocalisedField):
            return value
        obj = cls()
        if value:
            obj.__setattr__(obj.default_locale, str(value))

        return obj

    @default_locale.validator
    def _default_locale_validator(self, _, value: str) -> None:
        try:
            getattr(self, value)
        except AttributeError:
            raise ValueError(f"`{value}` is not a supported default localisation") from None

    def as_dict(self) -> str:
        return str(self)

    def to_locale_dict(self) -> dict:
        data = {}
        for attr in self.__attrs_attrs__:
            if attr.name != self.default_locale and "locale-code" in attr.metadata:
                if val := getattr(self, attr.name):
                    data[attr.metadata["locale-code"]] = val

        if not data:
            data = None  # handle discord being stupid
        return data


LocalizedField = LocalisedField
