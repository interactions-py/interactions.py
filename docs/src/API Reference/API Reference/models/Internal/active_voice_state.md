??? Hint "Example Usage:"
    ```python
    from interactions import slash_command, slash_option, OptionTypes, InteractionContext
    from interactions.api.voice.audio import AudioVolume


    @slash_command("play")
    @slash_option("song", "The song to play", OptionTypes.STRING, required=True)
    async def test_cmd(ctx: InteractionContext, song: str):
        await ctx.defer()

        if not ctx.voice_state:
            await ctx.author.voice.channel.connect() # (1)!

        await ctx.send(f"Playing {song}")
        await ctx.voice_state.play(AudioVolume(song)) # (2)!
    ```
    { .annotate }

    1.  This connects the bot to the author's voice channel if we are not already connected
    2.  Check out the [Voice Support Guide](/Guides/22 Voice.html) for more info on audio playback

::: interactions.models.internal.active_voice_state
