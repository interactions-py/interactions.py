import interactions

bot = interactions.Client(token=open("bot.token").read(), disable_sync=True, log_level=10)


@bot.event
async def on_ready():
    print("bot is now online.")


@bot.command(name="guild-command", description="haha guild go brrr", scope=852402668294766612)
async def guild_command(ctx: interactions.CommandContext):
    embed = interactions.Embed(
        title="Embed title",
        fields=[
            interactions.EmbedField(
                name="field name",
                value="values!",
            ),
            interactions.EmbedField(
                name="field name",
                value="values!",
            ),
            interactions.EmbedField(
                name="field name",
                value="values!",
            ),
        ],
    )
    await ctx.send("aloha senor.", embeds=embed)


@bot.command(
    name="global-command",
    description="ever wanted a global command? well, here it is!",
)
async def basic_command(ctx: interactions.CommandContext):
    fancy_schmancy = interactions.SelectMenu(
        custom_id="select_awesomeness",
        placeholder="please select UWU :(",
        options=[
            interactions.SelectOption(label="im pretty", value="prettiness"),
            interactions.SelectOption(label="im quirky", value="teenager"),
            interactions.SelectOption(label="im cool", value="hipster"),
        ],
        min_values=1,
        max_values=1,
    )
    await ctx.send("Global commands are back in action, baby!", components=fancy_schmancy)


@bot.component("select_awesomeness")
async def component_res(ctx: interactions.ComponentContext):
    await ctx.edit(
        "global pizza domination :pizza:.",
        components=interactions.SelectMenu(custom_id="x", disabled=True),
    )


# bot.load("simple_cog")
bot.start()
