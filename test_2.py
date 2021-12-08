import interactions


class CoolCogTest(interactions.Extension):
    def __init__(self, client):
        self.client = client

    @interactions.command(
        name="cog-command", description="testing in da cog.", scope=852402668294766612
    )
    async def cog_command(self, ctx):
        await ctx.send("is it gonna work?")


def setup(client):
    CoolCogTest(client)
