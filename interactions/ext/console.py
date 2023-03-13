import asyncio

import aiomonitor as aiomonitor

import interactions
from interactions import Extension

__all__ = ("Console",)


class Console(Extension):
    """
    Extension that starts the bot with the aiomonitor console active - notably giving you REPL for the bot

    To access the console, you need to connect to the port specified in the constructor, by default 501.
    On linux, you can do this with `nc localhost 501`, on windows you can use `telnet localhost 501`.

    For both platforms you can also use "python -m aiomonitor.cli -p 501" as a replacement for the above commands.

    Args:
        port: The port to start the aiomonitor on
        console_port: The port to start the aiomonitor console on
        **kwargs: The locals to make available in the console, by default this includes `client`, `bot` and `interactions`

    """

    def __init__(self, client: interactions.Client, port: int = 501, console_port: int = 502, **kwargs) -> None:
        self.client.astart = self.async_start_bot
        self.port = port  # 501 was chosen as windows throws a massive fit if you try to use the default port
        self.console_port = console_port
        self.locals = kwargs

    async def async_start_bot(self, token: str | None = None) -> None:
        """Starts the bot with the console active"""
        old_start = interactions.Client.astart

        _locals = self.locals | {
            "client": self.client,
            "bot": self.client,
            "interactions": interactions,
        }

        with aiomonitor.start_monitor(
            loop=asyncio.get_event_loop(), port=self.port, console_port=self.console_port, locals=_locals
        ) as monitor:
            self.client.logger.info(f"Started aiomonitor on {monitor._host}:{monitor._port}")

            await old_start(self.client, token)
