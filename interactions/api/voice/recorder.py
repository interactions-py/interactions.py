import asyncio
import io
import logging
import os
import shutil
import struct
import threading
import time
from asyncio import AbstractEventLoop
from collections import defaultdict
from typing import TYPE_CHECKING

import select

from interactions.api.voice.audio import RawInputAudio
from interactions.api.voice.audio_writer import AudioWriter
from interactions.api.voice.encryption import Decryption
from interactions.api.voice.opus import Decoder
from interactions.client.const import logger_name, Missing
from interactions.client.utils.input_utils import unpack_helper
from interactions.models.discord.snowflake import Snowflake_Type, to_snowflake_list

if TYPE_CHECKING:
    from interactions.models.internal.active_voice_state import ActiveVoiceState

__all__ = ("Recorder",)

log = logging.getLogger(logger_name)


class Recorder(threading.Thread):
    def __init__(self, v_state, loop, *, output_dir: str | None = None) -> None:
        super().__init__()
        self.daemon = True

        self.state: "ActiveVoiceState" = v_state
        self.loop: AbstractEventLoop = loop
        self.decrypter: Decryption = Decryption(self.state.ws.secret)
        self._decoders: dict[str, Decoder] = defaultdict(Decoder)

        # check if output_dir is a folder not a file
        if output_dir and not os.path.isdir(output_dir):
            raise ValueError("output_dir must be a directory")

        self.output_dir = output_dir
        self.audio: AudioWriter | None = None
        self.encoding = "mp3"
        self.recording = False
        self.used = False

        self.start_time = 0
        self.user_timestamps = {}
        self.recording_whitelist: list[Snowflake_Type] = []

        if not shutil.which("ffmpeg"):
            raise RuntimeError(
                "Unable to start recorder. FFmpeg was not found. Please add it to your project directory or PATH. (https://ffmpeg.org/)"
            )

    async def __aenter__(self) -> "Recorder":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop_recording()

    async def start_recording(self, *user_id: Snowflake_Type, output_dir: str | Missing = Missing) -> None:
        """
        Start recording audio from the current channel.

        Args:
            *user_id: The user_id(s) to record, if not specified everyone will be recorded.
            output_dir: The directory to save the audio to (overrides the constructor output_dir if specified)
        """
        if self.used:
            raise RuntimeError("Cannot reuse a recorder.")
        self.used = True

        if user_id:
            self.recording_whitelist = to_snowflake_list(unpack_helper(user_id))

        if output_dir is not Missing:
            self.output_dir = output_dir

        self.recording = True
        self.audio = AudioWriter(self, self.state.channel.id)
        self.start()
        self.start_time = time.monotonic()

    async def stop_recording(self) -> None:
        """Stop recording audio from the current channel."""
        self.recording = False

        def wait() -> None:
            self.audio.cleanup()
            self.audio.encode_audio(self.encoding)

        await asyncio.to_thread(wait)

    def decrypt(self, header: bytes, data: bytes) -> bytes:
        """
        An alias to call the decryption methods.

        Args:
            header: The payload header
            data: The payload data
        Returns:
              The decrypted payload
        """
        # a shorter alias to call
        return self.decrypter.decrypt(self.state.ws.selected_mode, header, data)

    def get_decoder(self, ssrc) -> Decoder:
        return self._decoders[ssrc]

    def get_user(self, ssrc: str) -> Snowflake_Type:
        """
        Get the corresponding user from a ssrc.

        Args:
            ssrc: The source to retrieve the user from
        Returns:
            A snowflake representing the user
        """
        return self.state.ws.user_ssrc_map.get(ssrc)["user_id"]

    def get_ssrc(self, user_id: Snowflake_Type) -> str:
        """
        Get the corresponding ssrc from a user.

        Args:
            user_id: The user to retrieve the ssrc from
        Returns:
            A string representing the ssrc
        """
        return next((ssrc for ssrc, user in self.state.ws.user_ssrc_map.items() if user["user_id"] == user_id), None)

    def __enter__(self) -> "Recorder":
        return self

    @property
    def output(self) -> dict[int, io.BytesIO | str]:
        """
        The output of the recorder.

        Returns:
            A dictionary of the user_id and the output file.
            Output file can be a BytesIO or a string (if output_dir is specified)
        """
        return self.audio.files if self.audio.finished.is_set() else {}

    @property
    def elapsed_time(self) -> float:
        return time.monotonic() - self.start_time

    def filter(self, *user_id: Snowflake_Type) -> None:
        """
        Filter the users that are being recorded.

        Args:
            *user_id: The user_id(s) to record
        """
        if not user_id:
            self.recording_whitelist = []
        self.recording_whitelist = to_snowflake_list(unpack_helper(user_id))

    def run(self) -> None:
        """The recording loop itself."""
        sock = self.state.ws.socket

        # purge any data that is already in the socket
        readable, _, _ = select.select([sock], [], [], 0)
        log.debug("Purging socket buffer")
        while readable and sock.recv(4096):
            readable, _, _ = select.select([sock], [], [], 0)
        log.debug("Socket buffer purged, starting recording")

        with self.audio:
            while self.recording:
                ready, _, err = select.select([sock], [], [sock], 0.01)
                if not ready:
                    if err:
                        log.error("Error while recording: %s", err)
                    continue

                data = sock.recv(4096)

                if 200 <= data[1] <= 204:
                    continue

                try:
                    raw_audio = RawInputAudio(self, data)
                    self.process_data(raw_audio)
                except Exception as ex:
                    log.error("Error while recording: %s", ex)

    def process_data(self, raw_audio: RawInputAudio) -> None:
        """
        Processes incoming audio data and writes it to the corresponding buffer.

        Args:
            raw_audio: The raw audio that has been received
        """
        if raw_audio.user_id is None:
            return  # usually the first frame when a user rejoins

        if self.recording_whitelist and raw_audio.user_id not in self.recording_whitelist:
            return

        decoder = self.get_decoder(raw_audio.ssrc)

        if raw_audio.ssrc not in self.user_timestamps:
            if last_timestamp := self.audio.last_timestamps.get(raw_audio.user_id, None):
                diff = raw_audio.timestamp - last_timestamp
                silence = int(diff * decoder.sample_rate)
                log.debug(
                    f"{self.state.channel.id}::{raw_audio.user_id} - User rejoined, adding {silence} silence frames ({diff} seconds)"
                )
            else:
                silence = 0

            self.user_timestamps.update({raw_audio.ssrc: raw_audio.timestamp})
        else:
            silence = raw_audio.timestamp - self.user_timestamps[raw_audio.ssrc]
            if silence < 0.1:
                silence = 0
            self.user_timestamps[raw_audio.ssrc] = raw_audio.timestamp

        raw_audio.pcm = struct.pack("<h", 0) * int(silence * decoder.sample_rate) * 2 + raw_audio.decoded

        self.audio.write(raw_audio, raw_audio.user_id)
