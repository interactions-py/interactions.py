from typing import Union, List, SupportsInt, Optional

import attrs

import interactions.models as models
from interactions.client.const import MISSING, Absent

__all__ = ("to_snowflake", "to_optional_snowflake", "to_snowflake_list", "SnowflakeObject", "Snowflake_Type")


# Snowflake_Type should be used in FUNCTION args of user-facing APIs (combined with to_snowflake to sanitize input)
# For MODEL id fields, just use int as type-hinting instead;
# For attr convertors: Use int() when API-facing conversion is expected,
# use to_snowflake when user should create this object
Snowflake_Type = Union[int, str, "SnowflakeObject", SupportsInt]


def to_snowflake(snowflake: Snowflake_Type) -> int:
    """
    Helper function to convert something into correct Discord snowflake int, gives more helpful errors Use internally to sanitize user input or in user- facing APIs (a must).

    For Discord-API - facing code, just int() is sufficient

    """
    try:
        snowflake = int(snowflake)
    except TypeError as e:
        raise TypeError(
            f"ID (snowflake) should be instance of int, str, SnowflakeObject, or support __int__. "
            f"Got '{snowflake}' ({type(snowflake)}) instead."
        ) from e
    except ValueError as e:
        raise ValueError(f"ID (snowflake) should represent int. Got '{snowflake}' ({type(snowflake)}) instead.") from e

    if 22 > snowflake.bit_length() > 64:
        raise ValueError(
            f"ID (snowflake) is not in correct Discord format! Bit length of int should be from 22 to 64 "
            f"Got '{snowflake}' (bit length {snowflake.bit_length()})"
        )

    return snowflake


def to_optional_snowflake(snowflake: Absent[Optional[Snowflake_Type]] = MISSING) -> Optional[int]:
    if snowflake is MISSING:
        return MISSING
    if snowflake is None:
        return None
    return to_snowflake(snowflake)


def to_snowflake_list(snowflakes: List[Snowflake_Type]) -> List[int]:
    return [to_snowflake(c) for c in snowflakes]


@attrs.define(eq=False, order=False, hash=False, slots=False)
class SnowflakeObject:
    id: int = attrs.field(repr=True, converter=to_snowflake, metadata={"docs": "Discord unique snowflake ID"})

    def __eq__(self, other: "SnowflakeObject") -> bool:
        if hasattr(other, "id"):
            other = other.id
        return self.id == other

    def __ne__(self, other: "SnowflakeObject") -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return self.id << 32

    def __int__(self) -> int:
        return self.id

    @property
    def created_at(self) -> "models.Timestamp":
        """
        Returns a timestamp representing the date-time this discord object was created.

        :Returns:

        """
        return models.Timestamp.from_snowflake(self.id)
