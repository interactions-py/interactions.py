# discord-py-slash-command
그냥 심심해서 만들어봤어요  

## 예제
```py
import discord
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.model import SlashContext

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
slash = SlashCommand(bot)


@slash.slash(name="test")
async def _test(ctx: SlashContext):
    embed = discord.Embed(title="임베드")
    await ctx.send(text="테스트", embeds=[embed])


bot.run("디스코드 토큰")
```

## 설치
그냥 알아서 클론해서 `discord_slash` 파일 갖다 쓰세요  
~~어차피 조금만 있으면 디코파이가 지원하겠죠~~