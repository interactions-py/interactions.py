---
search:
  boost: 3
---

# Voice Support

So you want to start playing some 🎵tunes🎶 in voice channels? Well let's get that going for you.

=== ":simple-windows: Windows"

    First you're going to want to get the voice dependencies installed:
    ```
    pip install discord.py-interactions[voice]
    ```

    Then you'll need to download [FFmpeg](https://ffmpeg.org) and place it in your project directory or PATH.

    Now you've got those; let's make a simple play command to get you started.

=== ":simple-linux: Linux"

    First you're going to want to get the voice dependencies installed:
    ```
    pip install discord.py-interactions[voice]
    ```

    Then you'll need to install the following packages:
    [libnacl](https://github.com/saltstack/libnacl), [libffi](https://github.com/libffi/libffi), and [FFmpeg](https://ffmpeg.org)

    :simple-debian: For debian based distros:
    ```
    sudo apt install ffmpeg libffi-dev libnacl-dev
    ```
    :simple-archlinux: For arch based distros:
    ```
    sudo pacman -S ffmpeg libffi libnacl
    ```
    :simple-fedora: For fedora based distros:
    ```
    sudo dnf install ffmpeg libffi-devel libsodium-devel
    ```

    If you get an error about "Could not find opus library," your distro may not have libopus installed. You'll need to find documentation for your distro on how to install it.


    Now you've got those; let's make a simple play command to get you started.

```python
import interactions
from interactions.api.voice.audio import AudioVolume


@interactions.slash_command("play", "play a song!")
@interactions.slash_option("song", "The song to play", 3, True)
async def play(self, ctx: interactions.SlashContext, song: str):
    if not ctx.voice_state:
        # if we haven't already joined a voice channel
        # join the authors vc
        await ctx.author.voice.channel.connect()

    # Get the audio using YTDL
    audio = await AudioVolume(song)
    await ctx.send(f"Now Playing: **{song}**")
    # Play the audio
    await ctx.voice_state.play(audio)
```

Now just join a voice channel, and type run the "play" slash command with a song of your choice.

Congratulations! You've got a music-bot.

## But what about local music?

If you want to play your own files, you can do that too! Create an `AudioVolume` object and away you go.

!!! note
    If your audio is already encoded, use the standard `Audio` object instead. You'll lose volume manipulation, however.

```python
import interactions
from interactions.api.voice.audio import AudioVolume


@interactions.slash_command("play", "play a song!")
async def play_file(ctx: interactions.SlashContext):
    audio = AudioVolume("some_file.wav")
    await ctx.voice_state.play(audio)
```

Check out [Active Voice State](/interactions.py/API Reference/API Reference/models/Internal/active_voice_state/) for a list of available methods and attributes.

# Voice Recording

So you've got a bot that can play music, but what about recording? Well, you're in luck! We've got you covered.

Let's start with a simple example:

```python
import asyncio
import interactions

@interactions.slash_command("record", "record some audio")
async def record(ctx: interactions.SlashContext):
    await ctx.defer()
    voice_state = await ctx.author.voice.channel.connect()

    # Start recording
    await voice_state.start_recording()
    await asyncio.sleep(10)
    await voice_state.stop_recording()
    await ctx.send("Here are your recordings", files=[interactions.File(file, file_name="user_id.mp3") for user_id, file in voice_state.recorder.output.items()])
```
This code will connect to the author's voice channel, start recording, wait 10 seconds, stop recording, and send a file for each user that was recorded.

But what if you didn't want to use `mp3` files? Well, you can change that too! Just pass the encoding you want to use to `start_recording`.

```python
await voice_state.start_recording(encoding="wav")
```

For a list of available encodings, check out Recorder's [documentation](/interactions.py/API Reference/API_Communication/voice/recorder.md)

Are you going to be recording for a long time? You are going to want to write the files to disk instead of keeping them in memory. You can do that too!

```python
await voice_state.start_recording(output_dir="folder_name")
```
This will write the files to the folder `folder_name` in the current working directory, please note that the library will not create the folder for you, nor will it delete the files when you're done.
