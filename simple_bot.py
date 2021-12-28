import interactions

bot = interactions.Client(token=open("bot.token").read(), log_level=-1)


@bot.event
async def on_ready():
    print("bot is now online.")


@bot.command(
    name="global-command",
    description="ever wanted a global command? well, here it is!",
)
async def basic_command(ctx: interactions.CommandContext):
    await ctx.send("Global commands are back in action, baby!")


# bot.load("simple_cog")
bot.start()
