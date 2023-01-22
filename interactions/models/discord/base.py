from typing import TYPE_CHECKING, Any, Dict, List, Type

import attrs

from interactions.client.const import T
from interactions.client.mixins.serialization import DictSerializationMixin
from interactions.client.utils.serializer import no_export_meta
from interactions.models.discord.snowflake import SnowflakeObject

if TYPE_CHECKING:
    from interactions.client import Client

__all__ = ("ClientObject", "DiscordObject")


@attrs.define(eq=False, order=False, hash=False, slots=False)
class ClientObject(DictSerializationMixin):
    """Serializable object that requires client reference."""

    _client: "Client" = attrs.field(repr=False, metadata=no_export_meta)

    @property
    def client(self) -> "Client":
        return self._client

    @property
    def bot(self) -> "Client":
        return self._client

    @classmethod
    def _process_dict(cls, data: Dict[str, Any], client: "Client") -> Dict[str, Any]:
        return super()._process_dict(data)

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any], client: "Client") -> T:
        data = cls._process_dict(data, client)
        return cls(client=client, **cls._filter_kwargs(data, cls._get_init_keys()))

    @classmethod
    def from_list(cls: Type[T], datas: List[Dict[str, Any]], client: "Client") -> List[T]:
        return [cls.from_dict(data, client) for data in datas]

    def update_from_dict(self, data) -> T:
        data = self._process_dict(data, self._client)
        for key, value in self._filter_kwargs(data, self._get_keys()).items():
            setattr(self, key, value)

        return self


@attrs.define(eq=False, order=False, hash=False, slots=False)
class DiscordObject(SnowflakeObject, ClientObject):
    pass
