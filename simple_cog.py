import interactions


class SimpleCog(interactions.Extension):
    def __init__(self, client) -> None:
        self.client = client

    # @interactions.extension_command(
    #     name="cog-command",
    #     description="wanna be in a cog? :)) ok.",
    #     scope=852402668294766612,
    # )
    async def cog_command(self, ctx):
        await ctx.send("we're a cog in the machine!")


def setup(client):
    SimpleCog(client)
