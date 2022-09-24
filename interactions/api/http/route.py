from typing import ClassVar, Optional

__all__ = ("Route",)


class Route:
    """
    A class representing how an HTTP route is structured.

    :ivar ClassVar[str] __api__: The HTTP route path.
    :ivar str method: The HTTP method.
    :ivar str path: The URL path.
    :ivar Optional[str] channel_id: The channel ID from the bucket if given.
    :ivar Optional[str] guild_id: The guild ID from the bucket if given.
    """

    __slots__ = ("method", "path", "channel_id", "guild_id")
    __api__: ClassVar[str] = "https://discord.com/api/v10"
    method: str
    path: str
    channel_id: Optional[str]
    guild_id: Optional[str]

    def __init__(self, method: str, path: str, **kwargs) -> None:
        r"""
        :param method: The HTTP request method.
        :type method: str
        :param path: The path of the HTTP/URL.
        :type path: str
        :param \**kwargs?: Optional keyword-only arguments to pass as information in the route.
        :type \**kwargs?: dict
        """
        self.method = method
        self.path = path.format(**kwargs)
        self.channel_id = kwargs.get("channel_id")
        self.guild_id = kwargs.get("guild_id")

    def get_bucket(self, shared_bucket: Optional[str] = None) -> str:
        """
        Returns the route's bucket. If shared_bucket is None, returns the path with major parameters.
        Otherwise, it relies on Discord's given bucket.

        :param shared_bucket: The bucket that Discord provides, if available.
        :type shared_bucket: Optional[str]

        :return: The route bucket.
        :rtype: str
        """
        return (
            f"{self.channel_id}:{self.guild_id}:{self.path}"
            if shared_bucket is None
            else f"{self.channel_id}:{self.guild_id}:{shared_bucket}"
        )

    @property
    def endpoint(self) -> str:
        """
        Returns the route's endpoint.

        :return: The route endpoint.
        :rtype: str
        """
        return f"{self.method}:{self.path}"
