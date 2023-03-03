import io
import logging
import subprocess  # noqa: S404
import threading
import time
from collections import defaultdict
from typing import TYPE_CHECKING

from interactions.client.const import logger_name

if TYPE_CHECKING:
    from interactions.api.voice.recorder import Recorder

__all__ = ("AudioWriter",)

log = logging.getLogger(logger_name)


class AudioWriter:
    SUPPORTED_ENCODINGS = (
        "mka",
        "mp3",
        "ogg",
        "pcm",
        "wav",
    )

    def __init__(self, recorder: "Recorder", channel_id: int, squash: bool = False) -> None:
        self._recorder = recorder
        self.channel_id = channel_id
        self.files: dict[int, io.BytesIO] = defaultdict(io.BytesIO)
        self.user_initial_timestamps: dict[int, float] = {}
        self.last_timestamps: dict[int, float] = {}

        self.done_recording = threading.Event()
        self.finished = threading.Event()

    def __enter__(self) -> "AudioWriter":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.cleanup()

    def write(self, data, user_id: int) -> None:
        """
        Write the incoming bytestream to the appropriate user's BytesIO

        Args:
            data: The data to be written
            user_id: The ID of the user
        Raises:
            RuntimeError: If audio is written after the Writer has stopped recording
        """
        if self.done_recording.is_set():
            raise RuntimeError("Attempted to write audio data after Writer is no longer recording.")

        if user_id not in self.files:
            if user_id is None:
                raise RuntimeError("Attempted to write audio without a known user_id")
            self.user_initial_timestamps[user_id] = time.perf_counter()
        self.last_timestamps[user_id] = time.perf_counter()

        file = self.files[user_id]
        file.write(data)

    def cleanup(self) -> None:
        """Cleanup after recording, ready for encoding."""
        if self.done_recording.is_set():
            return

        for file in self.files.values():
            file.seek(0)
        self.done_recording.set()

    def encode_audio(self, encoding: str) -> None:
        """
        Encode the recorded data into the desired format.

        Args:
            encoding: The format to encode to.
        Raises:
            ValueError: If a non-supported encoding is requested.
        """
        self.done_recording.wait()

        if encoding.lower() not in self.SUPPORTED_ENCODINGS:
            raise ValueError(
                f"`{encoding}` is not a supported encoding format. Supported Encodings are: {' '.join(self.SUPPORTED_ENCODINGS)}"
            )
        for user_id in self.files:
            getattr(self, f"_encode_{encoding.lower()}")(user_id)

        log.info(f"Finished encoding {self.channel_id}")
        self.finished.set()

    def __ffmpeg_encode(self, user_id: int, encoding: str) -> None:
        """
        An internal method to encode audio using ffmpeg.

        Args:
            user_id: The ID of the user's stream to encode.
            encoding: The encoding to use.
        """
        decoder = self._recorder.get_decoder(self._recorder.get_ssrc(user_id))
        args = f"ffmpeg -f s16le -ar {decoder.sample_rate} -ac {decoder.channels} -loglevel quiet -i - -f {encoding} pipe:1".split()
        process = subprocess.Popen(  # noqa: S603
            args,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )

        output = process.communicate(self.files[user_id].read())[0]
        output = io.BytesIO(output)
        output.seek(0)
        self.files[user_id] = output

    def _encode_mp3(self, user_id: int) -> None:
        """
        Encode a user's audio to mp3.

        Args:
            user_id: The ID of the user's stream to encode.
        """
        log.debug(f"Encoding audio stream for {user_id} as mp3")
        self.__ffmpeg_encode(user_id, "mp3")

    def _encode_ogg(self, user_id: int) -> None:
        """
        Encode a user's audio to ogg.

        Args:
            user_id: The ID of the user's stream to encode.
        """
        log.debug(f"Encoding audio stream for {user_id} as ogg")
        self.__ffmpeg_encode(user_id, "ogg")

    def _encode_mka(self, user_id: int) -> None:
        """
        Encode a user's audio to mka.

        Args:
            user_id: The ID of the user's stream to encode.
        """
        log.debug(f"Encoding audio stream for {user_id} as mka")
        self.__ffmpeg_encode(user_id, "matroska")

    def _encode_wav(self, user_id: int) -> None:
        """
        Encode a user's audio to wav.

        Args:
            user_id: The ID of the user's stream to encode.
        """
        log.debug(f"Encoding audio stream for {user_id} as wav")
        import wave

        out = io.BytesIO()

        with wave.open(out, "wb") as f:
            f.setnchannels(2)
            f.setsampwidth(2)
            f.setframerate(48000)
            f.writeframes(self.files[user_id].read())

        out.seek(0)
        self.files[user_id] = out

    def _encode_pcm(self, user_id: int) -> None:
        """
        Encode a user's audio to pcm.

        Args:
            user_id: The ID of the user's stream to encode.
        """
        # The audio is already in pcm format, this method is purely here to stop people asking for it.
        log.debug(f"Encoding audio stream for {user_id} as pcm")
        return
