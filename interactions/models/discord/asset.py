import re
from typing import TYPE_CHECKING, Optional, Union

import attrs

from interactions.client.utils.serializer import no_export_meta

if TYPE_CHECKING:
    from os import PathLike

    from interactions.client import Client

__all__ = ("Asset",)


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class Asset:
    """
    Represents a discord asset.

    Attributes:
        BASE str: The `cdn` address for assets
        url str: The URL of this asset
        hash Optional[str]: The hash of this asset

    """

    BASE = "https://cdn.discordapp.com"

    _client: "Client" = attrs.field(repr=False, metadata=no_export_meta)
    _url: str = attrs.field(repr=True)
    hash: Optional[str] = attrs.field(repr=True, default=None)

    @classmethod
    def from_path_hash(cls, client: "Client", path: str, asset_hash: str) -> "Asset":
        """
        Create an asset from a path and asset's hash.

        Args:
            client: The bot instance
            path: The CDN Endpoints for the type of asset.
            asset_hash: The hash representation of the target asset.

        Returns:
            A new Asset object

        """
        url = f"{cls.BASE}/{path.format(asset_hash)}"
        return cls(client=client, url=url, hash=asset_hash)

    @property
    def url(self) -> str:
        """The URL of this asset."""
        ext = ".gif" if self.animated else ".png"
        return f"{self._url}{ext}?size=4096"

    def as_url(self, *, extension: str | None = None, size: int = 4096) -> str:
        """
        Get the url of this asset.

        Args:
            extension: The extension to override the assets default with
            size: The size of asset to return

        Returns:
            A url for this asset with the given parameters
        """
        if not extension:
            extension = ".gif" if self.animated else ".png"
        elif not extension.startswith("."):
            extension = f".{extension}"

        return f"{self._url}{extension}?size={size}"

    @property
    def animated(self) -> bool:
        """True if this asset is animated."""
        # damn hashes with version numbers
        _hash = re.sub(r"^v\d+_", "", self.hash or "")
        return bool(self.hash) and _hash.startswith("a_")

    async def fetch(self, extension: Optional[str] = None, size: Optional[int] = None) -> bytes:
        """
        Fetch the asset from the Discord CDN.

        Args:
            extension: File extension based on the target image format
            size: The image size, can be any power of two between 16 and 4096.

        Returns:
            Raw byte array of the file

        Raises:
            ValueError: Incorrect file size if not power of 2 between 16 and 4096

        """
        if not extension:
            extension = ".gif" if self.animated else ".png"

        url = self._url + extension

        if size:
            if size == 0 or size & (size - 1) != 0:  # if not power of 2
                raise ValueError("Size should be a power of 2")
            if not 16 <= size <= 4096:
                raise ValueError("Size should be between 16 and 4096")

            url = f"{url}?size={size}"

        return await self._client.http.request_cdn(url, self)

    async def save(
        self,
        fd: Union[str, bytes, "PathLike", int],
        extension: Optional[str] = None,
        size: Optional[int] = None,
    ) -> int:
        """
        Save the asset to a local file.

        Args:
            fd: Destination path to save the file to.
            extension: File extension based on the target image format.
            size: The image size, can be any power of two between 16 and 4096.

        Returns:
            Status code result of file write

        """
        content = await self.fetch(extension=extension, size=size)
        with open(fd, "wb") as f:
            return f.write(content)
