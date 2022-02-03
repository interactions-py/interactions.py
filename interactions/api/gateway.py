import asyncio

try:
    from orjson import dumps, loads
except ImportError:
    from json import dumps, loads

# from asyncio import Event, create_task, get_event_loop, get_running_loop, new_event_loop, wait_for
from asyncio import Event, get_event_loop, get_running_loop, new_event_loop
from logging import Logger
from sys import platform, version_info
from typing import Any, Dict, List, Optional, Tuple

from aiohttp import WSMessage

from ..api.models.gw import Presence
from ..base import get_logger
from ..enums import InteractionType, OptionType
from ..models.misc import MISSING
from .dispatch import Listener
from .enums import OpCodeType
from .error import GatewayException
from .http import HTTPClient
from .models.flags import Intents

log: Logger = get_logger("gateway")


class WebSocketClient:
    """A class representing the client's connection to the Gateway via. WebSocket."""

    __slots__ = (
        "_loop",
        "_dispatch",
        "_http",
        "_client",
        "_closed",
        "_options",
        "_intents",
        "__trace",
        "__heartbeater",
        "__morgued",
        "session_id",
        "sequence",
        "ready",
        "_heartbeat_delay",
        "url",
        "__shard",
        "__presence",
        "__task",
    )

    def __init__(
        self,
        token: str,
        intents: Intents,
        session_id: Optional[int] = MISSING,
        sequence: Optional[int] = MISSING,
    ) -> None:
        """
        :param token: The token of the application for connecting to the Gateway.
        :type token: str
        :param intents: The Gateway intents of the application for event dispatch.
        :type intents: Intents
        :param session_id?: The ID of the session if trying to reconnect. Defaults to ``None``.
        :type session_id: Optional[int]
        :param sequence?: The identifier sequence if trying to reconnect. Defaults to ``None``.
        :type sequence: Optional[int]
        """
        try:
            self._loop = get_event_loop() if version_info < (3, 10) else get_running_loop()
        except RuntimeError:
            self._loop = new_event_loop()
        self._dispatch = Listener()
        self._http = HTTPClient(token)
        self._client = None
        self._closed = False
        self._options = {
            "max_msg_size": 1024 ** 2,
            "timeout": 60,
            "autoclose": False,
            "compress": 0,
        }
        self._intents = intents
        self.__heartbeater: Event = Event(loop=self._loop if version_info < (3, 10) else None)
        # self.__morgued = Event(loop=self._loop if version_info < (3, 10) else None)
        # self.__heartbeater = True  # event waits are painful, cba, using boolean instead.
        self.url = None

        self.session_id = None if session_id is MISSING else session_id
        self.sequence = None if sequence is MISSING else sequence
        self.ready = None
        self._heartbeat_delay: Optional[float] = None  # Stores heartbeat header metadata

        # persistent metadata post reconnection.
        self.__shard = None
        self.__presence = None

        self.__task = None

    async def __heartbeat_manager(self):
        """Manages the heartbeat loop."""
        while True:
            if self.__heartbeater.is_set():
                await self.__heartbeat_packet
                self.__heartbeater.clear()
                await asyncio.sleep(self._heartbeat_delay / 1000)
            else:
                log.debug("Heartbeat ACK not recieved, reconnecting to Gateway...")
                await self._client.close()
                await self._persistent_connection()
                break

    async def _persistent_connection(self):
        """Establishes a connection with the Gateway after a reconnect."""

        if self._closed:
            self._closed = False  # it's closed via the first failure. needs reopening for second.
        self._client = None  # discard.

        async with self._http._req._session.ws_connect(self.url, **self._options) as self._client:
            while not self._closed:
                stream = await self.__receive_packet_stream

                if stream is None:
                    continue
                if self._client.close_code:
                    raise GatewayException(self._client.close_code)

                await self._handle_connection(stream, self.__shard, self.__presence)

    async def _establish_connection(
        self, shard: Optional[List[int]] = MISSING, presence: Optional[Presence] = MISSING
    ) -> None:
        """Establishes a client connection with the Gateway."""
        self._options["headers"] = {"User-Agent": self._http._req._headers["User-Agent"]}
        url = await self._http.get_gateway()

        self.url = url
        self.__shard = shard
        self.__presence = presence

        async with self._http._req._session.ws_connect(url, **self._options) as self._client:
            while not self._closed:
                stream = await self.__receive_packet_stream

                if stream is None:
                    continue
                if self._client.close_code:
                    raise GatewayException(self._client.close_code)

                await self._handle_connection(stream, shard, presence)

    async def __close(self):
        """Properly closes the connection (currently, the heartbeat mgr)."""

        if self.__task:
            self.__task: asyncio.Task
            self.__task.cancel()  # cancel the heartbeat manager task.
        await self._client.close()  # close the ws connection. idk what code.
        await self._persistent_connection()  # restart it, then all should be well. I hope

    async def _handle_connection(
        self,
        stream: Dict[str, Any],
        shard: Optional[List[Tuple[int]]] = MISSING,
        presence: Optional[Presence] = MISSING,
    ) -> None:
        """Handles the client's connection with the Gateway."""
        op: Optional[int] = stream.get("op")
        event: Optional[str] = stream.get("t")
        data: Optional[Dict[str, Any]] = stream.get("d")

        if op != OpCodeType.DISPATCH:
            log.debug(data)

            if op == OpCodeType.HELLO:
                self._heartbeat_delay = data["heartbeat_interval"]
                self.__heartbeater.set()
                self.__task = asyncio.ensure_future(self.__heartbeat_manager())
                # The task will reinstate the client if the bool's false

                if not self.session_id:
                    await self.__identify_packet(shard, presence)
                else:
                    await self.__resume_packet
                # await self.__heartbeat_packet

                # the heartbeater's event is cleared by default. since it already sent a packet.....

                # self.__heartbeater._heartbeat.set()
                # await self._loop.call_later(
                #    self._heartbeat_delay, self.__heartbeater.set()
                # )  # todo: make this sync.
                # create_task(self.__heartbeater)
                # wait_for(self.__morgued, timeout=data["heartbeat_interval"], loop=self._loop)
            if op == OpCodeType.HEARTBEAT:
                await self.__heartbeat_packet
            if op == OpCodeType.HEARTBEAT_ACK:
                log.debug("HEARTBEAT_ACK")
                # self.__heartbeater = True
                self.__heartbeater.set()
            if op in (OpCodeType.INVALIDATE_SESSION, OpCodeType.RECONNECT):
                log.debug("INVALID_SESSION/RECONNECT")
                if not data or op == OpCodeType.RECONNECT:
                    await self.__close()
                else:
                    self.session_id = None
                    self.sequence = None
                    self._closed = True
                    await self.__close()
        elif event == "READY":
            self.session_id = data["session_id"]
            self.sequence = stream["s"]
            self._dispatch.dispatch("on_ready")
            log.debug(f"READY (session_id: {self.session_id}, seq: {self.sequence})")
        else:
            # log.debug(f"{event}: {dumps(data, indent=4, sort_keys=True)}")
            # above is omitted because of orjson's args and cross-compatibility.
            log.debug(f"{event}: {data}")
            self.handle_dispatch(event, data)

    def handle_dispatch(self, event: str, data: dict) -> None:
        """
        Handles the dispatched event data from a gateway event.

        :param event: The name of the event.
        :type event: str
        :param data: The data of the event.
        :type data: dict
        """

        def check_sub_command(option: dict) -> dict:
            kwargs: dict = {}
            if option["type"] == OptionType.SUB_COMMAND_GROUP:
                kwargs["sub_command_group"] = option["name"]
                if option.get("options"):
                    for group_option in option["options"]:
                        kwargs["sub_command"] = group_option["name"]
                        if group_option.get("options"):
                            for sub_option in group_option["options"]:
                                kwargs[sub_option["name"]] = sub_option["value"]
            elif option["type"] == OptionType.SUB_COMMAND:
                kwargs["sub_command"] = option["name"]
                if option.get("options"):
                    for sub_option in option["options"]:
                        kwargs[sub_option["name"]] = sub_option["value"]
            else:
                kwargs[option["name"]] = option["value"]

            return kwargs

        def check_sub_auto(option: dict) -> tuple:
            if option.get("options"):
                if option["type"] == OptionType.SUB_COMMAND_GROUP:
                    for group_option in option["options"]:
                        if group_option.get("options"):
                            for sub_option in group_option["options"]:
                                if sub_option.get("focused"):
                                    return sub_option["name"], sub_option["value"]
                elif option["type"] == OptionType.SUB_COMMAND:
                    for sub_option in option["options"]:
                        if sub_option.get("focused"):
                            return sub_option["name"], sub_option["value"]
            elif option.get("focused"):
                return option["name"], option["value"]

        if event != "TYPING_START":
            name: str = event.lower()
            path: str = "interactions"
            path += ".models" if event == "INTERACTION_CREATE" else ".api.models"

            if event != "INTERACTION_CREATE":
                try:
                    lst_names: list = [piece.capitalize() for piece in name.split("_")]
                    _name: str = (
                        lst_names[0]
                        if len(lst_names) < 3
                        else "".join(piece for piece in lst_names[:-1])
                    )
                    log.debug(f"Dispatching object {_name} from event {name}")
                    obj: object = getattr(
                        __import__(path),
                        _name,
                    )
                    if "_create" in event.lower() or "_add" in event.lower():
                        data["_client"] = self._http
                    self._dispatch.dispatch(f"on_{name}", obj(**data))  # noqa
                except AttributeError as error:  # noqa
                    log.fatal(f"You're missing a data model for the event {name}: {error}")
            else:
                if not data.get("type"):
                    log.warning("Context data is being constructed but there's no type. Skipping.")
                else:
                    context = self.contextualize(data)
                    _name: str
                    _args: list = [context]
                    _kwargs: dict = dict()
                    if data["type"] == InteractionType.APPLICATION_COMMAND:
                        _name = f"command_{context.data.name}"
                        if context.data._json.get("options"):
                            if context.data.options:
                                for option in context.data.options:
                                    _kwargs.update(
                                        check_sub_command(
                                            option if isinstance(option, dict) else option._json
                                        )
                                    )
                    elif data["type"] == InteractionType.MESSAGE_COMPONENT:
                        _name = f"component_{context.data.custom_id}"
                        if context.data._json.get("values"):
                            _args.append(context.data.values)
                    elif data["type"] == InteractionType.APPLICATION_COMMAND_AUTOCOMPLETE:
                        _name = f"autocomplete_{context.data.id}"
                        if context.data._json.get("options"):
                            if context.data.options:
                                for option in context.data.options:
                                    add_name, add_args = check_sub_auto(
                                        option if isinstance(option, dict) else option._json
                                    )
                                    if add_name:
                                        _name += f"_{add_name}"
                                    if add_args:
                                        _args.append(add_args)
                    elif data["type"] == InteractionType.MODAL_SUBMIT:
                        _name = f"modal_{context.data.custom_id}"
                        if hasattr(context.data, "components"):
                            if context.data.components:
                                for component in context.data.components:
                                    for _value in component.components:
                                        _args.append(_value["value"])

                    self._dispatch.dispatch(_name, *_args, **_kwargs)

            self._dispatch.dispatch("raw_socket_create", data)

    def contextualize(self, data: dict) -> object:
        """
        Takes raw data given back from the gateway
        and gives "context" based off of what it is.

        :param data: The data from the gateway.
        :type data: dict
        :return: The context object.
        :rtype: object
        """
        if data["type"] != InteractionType.PING:
            _context: str = ""

            if data["type"] in (
                InteractionType.APPLICATION_COMMAND,
                InteractionType.APPLICATION_COMMAND_AUTOCOMPLETE,
                InteractionType.MODAL_SUBMIT,
            ):
                _context = "CommandContext"
            elif data["type"] == InteractionType.MESSAGE_COMPONENT:
                _context = "ComponentContext"

            data["client"] = self._http
            context: object = getattr(__import__("interactions.context"), _context)
            return context(**data)

    @property
    async def __receive_packet_stream(self) -> Optional[Dict[str, Any]]:
        """
        Receives a stream of packets sent from the Gateway.

        :return: The packet stream.
        :rtype: Optional[Dict[str, Any]]
        """
        packet: WSMessage = await self._client.receive()
        return loads(packet.data) if packet and isinstance(packet.data, str) else None

    async def _send_packet(self, data: Dict[str, Any]) -> None:
        """
        Sends a packet to the Gateway.

        :param data: The data to send to the Gateway.
        :type data: Dict[str, Any]
        """
        packet: str = dumps(data).decode("utf-8") if isinstance(data, dict) else data
        await self._client.send_str(packet)
        log.debug(packet)

    async def __identify_packet(
        self, shard: Optional[List[int]] = MISSING, presence: Optional[Presence] = MISSING
    ) -> None:
        """
        Sends an ``IDENTIFY`` packet to the gateway.

        :param shard?: The shard ID to identify under.
        :type shard: Optional[int]
        :param presence?: The presence to change the bot to on identify.
        :type presence: Optional[Presence]
        """
        payload: dict = {
            "op": OpCodeType.IDENTIFY,
            "d": {
                "token": self._http.token,
                "intents": self._intents.value,
                "properties": {
                    "$os": platform,
                    "$browser": "interactions.py",
                    "$device": "interactions.py",
                },
            },
        }

        if isinstance(shard, List):
            if len(shard) >= 1:
                payload["d"]["shard"] = shard
        if isinstance(presence, Presence):
            payload["d"]["presence"] = presence._json

        log.debug(f"IDENTIFYING: {payload}")
        await self._send_packet(payload)
        log.debug("IDENTIFY")

    @property
    async def __resume_packet(self) -> None:
        """Sends a ``RESUME`` packet to the gateway."""
        payload: dict = {
            "op": OpCodeType.RESUME,
            "d": {"token": self._http.token, "seq": self.sequence, "session_id": self.session_id},
        }
        log.debug(f"RESUMING: {payload}")
        await self._send_packet(payload)
        log.debug("RESUME")

    @property
    async def __heartbeat_packet(self) -> None:
        """Sends a ``HEARTBEAT`` packet to the gateway."""
        payload: dict = {"op": OpCodeType.HEARTBEAT, "d": self.sequence}
        await self._send_packet(payload)
        log.debug("HEARTBEAT")
