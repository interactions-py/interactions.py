from interactions import Client, listen, File

bot = Client()


@listen()
async def on_startup():
    print(f"Logged in as {bot.user}")


bot.start("NzAxMzQ3ODc4MzExODIxMzcz.Gc0rqV.PH6XmX0VFBmQHZVieaAfNB6paUiThcSliqhbjk")
