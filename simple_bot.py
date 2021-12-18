import interactions

bot = interactions.Client(token=open(".token").read())


@bot.event
async def on_ready():
    print("bot is now online.")


@bot.command(
    name="basic-command",
    description="ever wanted a basic command? well, here it is!",
    scope=852402668294766612,
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="option",
            description="please PLEASE write in me! UwU :(",
            required=True,
        )
    ],
)
async def basic_command(ctx, option):
    await ctx.send(f"{option}")


bot.load("simple_cog")
bot.start()
