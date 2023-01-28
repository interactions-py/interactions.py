??? Hint "Example Usage:"
    ```python
    from naff import slash_command, cooldown, Buckets

    @slash_command(name='cmd')
    @cooldown(Buckets.user, 1, 10) # (1)!
    async def some_command(ctx):
        ...
    ```
    { .annotate }

    1.  This will create a cooldown for each user; allowing them to use the command once every 10 seconds

::: interactions.models.internal.cooldowns
