import interactions


class SimpleCog(interactions.Extension):
    def __init__(self, client) -> None:
        super().__init__(client)

    # @command(
    #     name="cog-command",
    #     description="wanna be in a cog? :)) ok.",
    #     scope=852402668294766612,
    # )
    # async def cog_command(self, ctx):
    #     await ctx.send("we're a cog in the machine!")


def startup(client):
    SimpleCog(client)
