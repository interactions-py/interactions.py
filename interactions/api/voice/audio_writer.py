import io
import os
import subprocess
import threading
import time
from collections import defaultdict
from contextlib import suppress
from typing import TYPE_CHECKING, BinaryIO

from interactions.api.voice.audio import AudioBuffer, RawInputAudio
from interactions.client.const import get_logger

if TYPE_CHECKING:
    from interactions.api.voice.recorder import Recorder

__all__ = ("AudioWriter",)

log = get_logger()


class AudioWriter:
    SUPPORTED_ENCODINGS = (
        "flac",
        "mka",
        "mp3",
        "ogg",
        "pcm",
        "wav",
    )

    def __init__(self, recorder: "Recorder", channel_id: int, squash: bool = False) -> None:
        self._recorder = recorder
        self.channel_id = channel_id

        self.output_dir = recorder.output_dir
        self.buffers: dict[int, AudioBuffer] = defaultdict(AudioBuffer)
        self.files: dict[int, io.BytesIO | BinaryIO | str] = defaultdict(io.BytesIO)

        self.buffer_task: threading.Thread = (
            threading.Thread(target=self._buffer_writer, daemon=True) if self.output_dir else None
        )

        self.user_initial_timestamps: dict[int, float] = {}
        self.last_timestamps: dict[int, float] = {}

        self._recording_complete = threading.Event()  # set when no more audio is being written
        self.done_recording = threading.Event()  # set when the recording is done, and all buffers are empty
        self.finished = threading.Event()

    def __enter__(self) -> "AudioWriter":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.cleanup()

    def write(self, audio: RawInputAudio, user_id: int) -> None:
        """
        Write the incoming bytestream to the appropriate user's BytesIO

        Args:
            audio: The incoming audio data
            user_id: The ID of the user
        Raises:
            RuntimeError: If audio is written after the Writer has stopped recording
        """
        if self._recording_complete.is_set():
            raise RuntimeError("Attempted to write audio data after Writer is no longer recording.")

        if user_id is None:
            raise RuntimeError("Attempted to write audio without a known user_id")

        if user_id not in self.user_initial_timestamps:
            self.user_initial_timestamps[user_id] = audio.timestamp

        self.last_timestamps[user_id] = audio.timestamp

        if self.output_dir:
            # if we have an output directory, we want to write to a file
            if user_id not in self.files:
                self.files[user_id] = open(f"{self.output_dir}/{self.channel_id}_{user_id}.pcm", "wb+")
                self.files[user_id].truncate(0)
            if not self.buffer_task.is_alive():
                log.debug("Starting buffer writer thread")
                self.buffer_task.start()
            self.buffers[user_id].extend(audio.pcm)
        else:
            # we want to write to memory
            self.files[user_id].write(audio.pcm)

    def _buffer_writer(self) -> None:
        """Write the buffered data to the file."""
        while not self._recording_complete.is_set() or all(len(buffer) != 0 for buffer in self.buffers.copy().values()):
            for user_id, buffer in self.buffers.items():
                if len(buffer) == 0:
                    continue
                if user_id not in self.files:
                    log.debug(f"File for {user_id} is not open, skipping")
                    continue
                self.files[user_id].write(buffer.read_max(1024))
            if all(len(buffer) == 0 for buffer in self.buffers.copy().values()):
                time.sleep(0.05)

        log.debug("Buffer writer thread finished")
        for file in self.files.values():
            file.flush()
            file.seek(0)
        self.done_recording.set()

    def cleanup(self) -> None:
        """Cleanup after recording, ready for encoding."""
        if self._recording_complete.is_set():
            return

        self._recording_complete.set()

        if self.output_dir and self.buffer_task.is_alive():
            self.done_recording.wait()
        self.done_recording.set()

        for file in self.files.values():
            file.seek(0)

    def encode_audio(self, encoding: str) -> None:
        """
        Encode the recorded data into the desired format.

        Args:
            encoding: The format to encode to.

        Raises:
            ValueError: If a non-supported encoding is requested.
        """
        self._recording_complete.wait()
        if self.output_dir and self.buffer_task.is_alive():
            self.done_recording.wait()
        self.done_recording.set()

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
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )

        output = process.communicate(self.files[user_id].read())[0]
        if self.output_dir:
            with open(f"{self.output_dir}/{self.channel_id}_{user_id}.{encoding}", "wb+") as f:
                f.write(output)
            with suppress(FileNotFoundError, PermissionError):
                self.files[user_id].close()
                os.remove(f"{self.output_dir}/{self.channel_id}_{user_id}.pcm")
            output = f"{self.output_dir}/{self.channel_id}_{user_id}.{encoding}"
        else:
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

        if self.output_dir:
            with open(f"{self.output_dir}/{self.channel_id}_{user_id}.wav", "wb+") as f:
                f.write(out.read())
            with suppress(FileNotFoundError, PermissionError):
                self.files[user_id].close()
                os.remove(f"{self.output_dir}/{self.channel_id}_{user_id}.pcm")
            out = f"{self.output_dir}/{self.channel_id}_{user_id}.wav"
        self.files[user_id] = out

    def _encode_flac(self, user_id: int) -> None:
        """
        Encode a user's audio to FLAC.

        Args:
            user_id: The ID of the user's stream to encode.
        """
        log.debug(f"Encoding audio stream for {user_id} as flac")
        self.__ffmpeg_encode(user_id, "flac")

    def _encode_pcm(self, user_id: int) -> None:
        """
        Encode a user's audio to pcm.

        Args:
            user_id: The ID of the user's stream to encode.
        """
        # The audio is already in pcm format, this method is purely here to stop people asking for it.
        log.debug(f"Encoding audio stream for {user_id} as pcm")
        path = f"{self.output_dir}/{self.files[user_id].name.split(os.sep)[-1]}"

        self.files[user_id].close()
        self.files[user_id] = path

        return
