import io
import logging
import shutil
import struct
import threading
import time
from asyncio import AbstractEventLoop
from collections import defaultdict
from typing import TYPE_CHECKING


from interactions.api.voice.audio import RawInputAudio
from interactions.api.voice.audio_writer import AudioWriter
from interactions.api.voice.encryption import Decryption
from interactions.api.voice.opus import Decoder
from interactions.client.const import logger_name
from interactions.client.utils.input_utils import unpack_helper
from interactions.models.discord.snowflake import Snowflake_Type, to_snowflake_list

if TYPE_CHECKING:
    from interactions.models.internal.active_voice_state import ActiveVoiceState

__all__ = ("Recorder",)

log = logging.getLogger(logger_name)


class Recorder(threading.Thread):
    def __init__(self, v_state, loop) -> None:
        super().__init__()
        self.daemon = True

        self.state: "ActiveVoiceState" = v_state
        self.loop: AbstractEventLoop = loop
        self.decrypter: Decryption = Decryption(self.state.ws.secret)
        self._decoders: dict[str, Decoder] = defaultdict(Decoder)

        self.audio = AudioWriter(self, self.state.channel.id)
        self.encoding = "mp3"
        self.recording = False

        self.user_timestamps = {}

        self.recording_whitelist: list[Snowflake_Type] = []

        if not shutil.which("ffmpeg"):
            raise RuntimeError(
                "Unable to start recorder. FFmpeg was not found. Please add it to your project directory or PATH. (https://ffmpeg.org/)"
            )

    @property
    def output(self) -> dict[int, io.BytesIO]:
        """The encoded audio this"""
        if self.audio.finished.is_set():
            return self.audio.files
        else:
            return {}

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

    def __enter__(self) -> "Recorder":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.recording = False

    def filter(self, *user_id: Snowflake_Type) -> None:
        """
        Filter the users that are being recorded.
        Args:
            *user_id: The user_id(s) to record
        """
        if not user_id:
            self.recording_whitelist = []
        self.recording_whitelist = to_snowflake_list(unpack_helper(user_id))

    def start_recording(self, *user_id: Snowflake_Type) -> None:
        """Start recording audio from the current channel.
        Args:
            *user_id: The user_id(s) to record, if not specified everyone will be recorded.
        """
        if user_id:
            self.recording_whitelist = to_snowflake_list(unpack_helper(user_id))

        self.recording = True
        self.start()

    def stop_recording(self) -> None:
        """Stop recording audio from the current channel."""
        self.recording = False
        self.audio.done_recording.wait()
        self.audio.encode_audio(self.encoding)

    def run(self) -> None:
        """The recording loop itself."""
        with self.audio:
            while self.recording:
                data = self.state.ws.socket.recv(4096)

                if 200 <= data[1] <= 204:
                    continue

                raw_audio = RawInputAudio(self, data)
                self.process_data(raw_audio)

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

        if raw_audio.ssrc not in self.user_timestamps:
            if last_timestamp := self.audio.last_timestamps.get(raw_audio.user_id, None):
                diff = time.perf_counter() - last_timestamp
                silence = int(diff * self.get_decoder(raw_audio.ssrc).sample_rate)
                log.debug(f"{self.state.channel.id}::{raw_audio.user_id} - User rejoined, adding {silence} silence frames ({diff} seconds)")
            else:
                silence = 0

            self.user_timestamps.update({raw_audio.ssrc: raw_audio.timestamp})
        else:
            silence = raw_audio.timestamp - self.user_timestamps[raw_audio.ssrc] - 960
            self.user_timestamps[raw_audio.ssrc] = raw_audio.timestamp

        data = struct.pack("<h", 0) * silence * 2 + raw_audio.pcm

        self.audio.write(data, raw_audio.user_id)
