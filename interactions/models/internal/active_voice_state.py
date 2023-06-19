import asyncio
from io import BytesIO
from typing import Optional, TYPE_CHECKING

import attrs
from discord_typings import VoiceStateData

from interactions.api.voice.player import Player
from interactions.api.voice.recorder import Recorder
from interactions.api.voice.voice_gateway import VoiceGateway
from interactions.client.const import MISSING, Missing
from interactions.client.errors import VoiceAlreadyConnected, VoiceConnectionTimeout
from interactions.client.utils import optional
from interactions.models.discord.enums import Intents
from interactions.models.discord.snowflake import Snowflake_Type, to_snowflake
from interactions.models.discord.voice_state import VoiceState

if TYPE_CHECKING:
    from interactions.api.voice.audio import BaseAudio
    from interactions.api.gateway.gateway import GatewayClient

__all__ = ("ActiveVoiceState",)


@attrs.define(eq=False, order=False, hash=False, kw_only=True)
class ActiveVoiceState(VoiceState):
    ws: Optional[VoiceGateway] = attrs.field(repr=False, default=None)
    """The websocket for this voice state"""
    player: Optional[Player] = attrs.field(repr=False, default=None)
    """The playback task that broadcasts audio data to discord"""
    recorder: Optional[Recorder] = attrs.field(default=None)
    """A recorder task to capture audio from discord"""
    _volume: float = attrs.field(repr=False, default=0.5)

    # standard voice states expect this data, this voice state lacks it initially; so we make them optional
    user_id: "Snowflake_Type" = attrs.field(repr=False, default=MISSING, converter=optional(to_snowflake))
    _guild_id: Optional["Snowflake_Type"] = attrs.field(repr=False, default=None, converter=optional(to_snowflake))
    _member_id: Optional["Snowflake_Type"] = attrs.field(repr=False, default=None, converter=optional(to_snowflake))

    def __attrs_post_init__(self) -> None:
        # jank line to handle the two inherently incompatible data structures
        self._member_id = self.user_id = self._client.user.id

    def __del__(self) -> None:
        if self.connected:
            self.ws.close()
        if self.player:
            self.player.stop()

    def __repr__(self) -> str:
        return f"<ActiveVoiceState: channel={self.channel} guild={self.guild} volume={self.volume} playing={self.playing} audio={self.current_audio}>"

    @property
    def current_audio(self) -> Optional["BaseAudio"]:
        """The current audio being played"""
        if self.player:
            return self.player.current_audio

    @property
    def volume(self) -> float:
        """Get the volume of the player"""
        return self._volume

    @volume.setter
    def volume(self, value) -> None:
        """Set the volume of the player"""
        if value < 0.0:
            raise ValueError("Volume may not be negative.")
        self._volume = value
        if self.player and hasattr(self.player.current_audio, "volume"):
            self.player.current_audio.volume = value

    @property
    def paused(self) -> bool:
        """Is the player currently paused"""
        return self.player.paused if self.player else False

    @property
    def playing(self) -> bool:
        """Are we currently playing something?"""
        # noinspection PyProtectedMember
        return bool(self.player and self.current_audio and not self.player.stopped and self.player._resume.is_set())

    @property
    def stopped(self) -> bool:
        """Is the player stopped?"""
        return self.player.stopped if self.player else True

    @property
    def connected(self) -> bool:
        """Is this voice state currently connected?"""
        # noinspection PyProtectedMember
        return False if self.ws is None else self.ws._closed.is_set()

    @property
    def gateway(self) -> "GatewayClient":
        return self._client.get_guild_websocket(self._guild_id)

    async def wait_for_stopped(self) -> None:
        """Wait for the player to stop playing."""
        if self.player:
            # noinspection PyProtectedMember
            await self.player._stopped.wait()

    async def _ws_connect(self) -> None:
        """Runs the voice gateway connection"""
        async with self.ws:
            try:
                await self.ws.run()
            finally:
                if self.playing:
                    await self.stop()

    async def ws_connect(self) -> None:
        """Connect to the voice gateway for this voice state"""
        self.ws = VoiceGateway(self._client._connection_state, self._voice_state.data, self._voice_server.data)

        _ = asyncio.create_task(self._ws_connect())
        await self.ws.wait_until_ready()

    def _guild_predicate(self, event) -> bool:
        return int(event.data["guild_id"]) == self._guild_id

    async def connect(self, timeout: int = 5) -> None:
        """
        Establish the voice connection.

        Args:
            timeout: How long to wait for state and server information from discord

        Raises:
            VoiceAlreadyConnected: if the voice state is already connected to the voice channel
            VoiceConnectionTimeout: if the voice state fails to connect

        """
        if self.connected:
            raise VoiceAlreadyConnected

        if Intents.GUILD_VOICE_STATES not in self._client.intents:
            raise RuntimeError("Cannot connect to voice without the GUILD_VOICE_STATES intent.")

        tasks = [
            asyncio.create_task(
                self._client.wait_for("raw_voice_state_update", self._guild_predicate, timeout=timeout)
            ),
            asyncio.create_task(
                self._client.wait_for("raw_voice_server_update", self._guild_predicate, timeout=timeout)
            ),
        ]

        await self.gateway.voice_state_update(self._guild_id, self._channel_id, self.self_mute, self.self_deaf)

        self.logger.debug("Waiting for voice connection data...")

        try:
            self._voice_state, self._voice_server = await asyncio.gather(*tasks)
        except asyncio.TimeoutError:
            raise VoiceConnectionTimeout from None

        self.logger.debug("Attempting to initialise voice gateway...")
        await self.ws_connect()

    async def disconnect(self) -> None:
        """Disconnect from the voice channel."""
        await self.gateway.voice_state_update(self._guild_id, None)

    async def move(self, channel: "Snowflake_Type", timeout: int = 5) -> None:
        """
        Move to another voice channel.

        Args:
            channel: The channel to move to
            timeout: How long to wait for state and server information from discord

        """
        target_channel = to_snowflake(channel)
        if target_channel != self._channel_id:
            already_paused = self.paused
            if self.player:
                self.player.pause()

            self._channel_id = target_channel
            await self.gateway.voice_state_update(self._guild_id, self._channel_id, self.self_mute, self.self_deaf)

            self.logger.debug("Waiting for voice connection data...")
            try:
                await self._client.wait_for("raw_voice_state_update", self._guild_predicate, timeout=timeout)
            except asyncio.TimeoutError:
                await self._close_connection()
                raise VoiceConnectionTimeout from None

            if self.player and not already_paused:
                self.player.resume()

    async def stop(self) -> None:
        """Stop playback."""
        self.player.stop()
        await self.player._stopped.wait()

    def pause(self) -> None:
        """Pause playback"""
        self.player.pause()

    def resume(self) -> None:
        """Resume playback."""
        self.player.resume()

    async def play(self, audio: "BaseAudio") -> None:
        """
        Start playing an audio object.

        Waits for the player to stop before returning.

        Args:
            audio: The audio object to play
        """
        if self.player:
            await self.stop()

        with Player(audio, self, asyncio.get_running_loop()) as self.player:
            self.player.play()
            await self.wait_for_stopped()

    def play_no_wait(self, audio: "BaseAudio") -> None:
        """
        Start playing an audio object, but don't wait for playback to finish.

        Args:
            audio: The audio object to play
        """
        _ = asyncio.create_task(self.play(audio))

    def create_recorder(self) -> Recorder:
        """Create a recorder instance."""
        if not self.recorder:
            self.recorder = Recorder(self, asyncio.get_running_loop())
        return self.recorder

    async def start_recording(self, encoding: Optional[str] = None, *, output_dir: str | Missing = Missing) -> Recorder:
        """
        Start recording the voice channel.

        If no recorder exists, one will be created.

        Args:
            encoding: What format the audio should be encoded to.
            output_dir: The directory to save the audio to
        """
        if not self.recorder:
            self.recorder = Recorder(self, asyncio.get_running_loop())

        if self.recorder.used:
            if self.recorder.recording:
                raise RuntimeError("Another recording is still in progress, please stop it first.")
            self.recorder = Recorder(self, asyncio.get_running_loop())

        if encoding is not None:
            self.recorder.encoding = encoding

        await self.recorder.start_recording(output_dir=output_dir)
        return self.recorder

    async def stop_recording(self) -> dict[int, BytesIO]:
        """
        Stop the recording.

        Returns:
            dict[snowflake, BytesIO]: The recorded audio
        """
        if not self.recorder or not self.recorder.recording or not self.recorder.audio:
            raise RuntimeError("No recorder is running!")
        await self.recorder.stop_recording()

        self.recorder.audio.finished.wait()
        return self.recordings

    @property
    def recordings(self) -> dict[int, BytesIO]:
        return self.recorder.output if self.recorder else {}

    async def _voice_server_update(self, data) -> None:
        """
        An internal receiver for voice server events.

        Args:
            data: voice server data
        """
        self.ws.set_new_voice_server(data)

    async def _voice_state_update(
        self,
        before: Optional[VoiceState],
        after: Optional[VoiceState],
        data: Optional[VoiceStateData],
    ) -> None:
        """
        An internal receiver for voice server state events.

        Args:
            before: The previous voice state
            after: The current voice state
            data: Raw data from gateway
        """
        if after is None:
            # bot disconnected
            self.logger.info(f"Disconnecting from voice channel {self._channel_id}")
            await self._close_connection()
            self._client.cache.delete_bot_voice_state(self._guild_id)
            return

        self.update_from_dict(data)

    async def _close_connection(self) -> None:
        """Close the voice connection."""
        if self.playing:
            await self.stop()
        if self.connected:
            self.ws.close()
