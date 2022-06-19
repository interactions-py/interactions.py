from typing import Optional, Union
from aiohttp import BasicAuth
import re

__all__ = ("ProxyConfig",)


class ProxyConfig:
    """
    The ProxyConfig class. This represents a simple configuration structure for a proxy to connect through.
    """
    def __init__(
        self,
        *args,
        scheme: Optional[str] = "https",
        host: Optional[str] = None,
        port: Optional[Union[str, int]] = None,
        user: Optional[str] = None,
        password: Optional[str] = None
    ) -> None:
        """
        Initialize a new ProxyConfig instance.

        :param scheme: The proxy scheme. Should be either "http" or "https"
        :type scheme: Optional[str]
        :param host: The proxy hostname/IP.
        :type host: str
        :param port: The port the proxy server is listening to.
        :type port: Union[str, int]
        :param user: The username of the proxy.
        :type user: Optional[str]
        :param password: The password of the proxy.
        :type password: Optional[str]
        """
        if len(args) > 1:
            raise TypeError(
                "ProxyConfig can only be initialized with one positional argument " +
                "of string format: [http/https]://[login]:[password]@host:port"
            )
        elif len(args) == 1 and isinstance(args[0], str):
            _re_proxy = re.search(
                "^((?P<scheme>[^:/?#]+):(?=//))?(//)?(((?P<login>[^:]+)(?::(?P<password>[^@]+)?)?@)?(?P<host>[^@/?#:]*)(?::(?P<port>[0-9]+)?)?)?",  # noqa: E501
                args[0],
            )
            self.scheme = _re_proxy["scheme"] or scheme
            self.host = _re_proxy["host"] or host
            self.port = _re_proxy["port"] or str(port)
            self.auth = BasicAuth(_re_proxy["login"] or user, _re_proxy["password"] or password) \
                if user and password else None
        else:
            self.scheme = scheme
            self.host = host
            self.port = str(port)
            self.auth = BasicAuth(user, password) if user and password else None

        if not self.host or not self.port:
            raise ValueError("ProxyConfig must have host and port")

    def __str__(self) -> str:
        return f"{self.scheme}://{self.host}:{self.port}"
