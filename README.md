# interactions.py

![image](https://img.shields.io/pypi/dm/discord-py-slash-command.svg)
![image](https://img.shields.io/pypi/pyversions/discord-py-interactions.svg)
![image](https://img.shields.io/pypi/v/discord-py-interactions.svg)
![image](https://readthedocs.org/projects/interactionspy/badge/?version=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![image](https://discord.com/api/guilds/789032594456576001/embed.png)

------------------------------------------------------------------------

A highly extensible, easy to use, and feature complete bot framework for Discord. 
`Interactions.py` is the culmination of years of experience in the Discord API and bot development. 
This library has been built from the ground up with community feedback and suggestions in mind. 

## Key Features
- ✅ 100% coverage of the application commands API
- ✅ Dynamic cache with TTL support
- ✅ Modern and Pythonic API
- ✅ Proper rate-limit handling
- ✅ Feature parity with most other Discord API wrappers
- ✅ Easy to use
- ✅ Event-Triggered callbacks 
- ✅ Global decorators 
- ✅ Easily extendable
- ✅ Fully automated command synchronisation 

## Extensibility

So the stock library doesn't do what you want? No problem! Builtin extensions are available to extend the functionality of the library. 
And if none of those strike your fancy there are a myriad of other extension libraries available.

Just type `bot.load("extension")`

<details>
    <summary>Extensions</summary>

   ### Prefixed Commands
    
   Prefixed commands, message commands, or legacy commands. 
   Whatever you want to call them, by default the `interactions.py` library will not handle these. But rest assured this extension will get you going
    
  - ✅ Hybrid Commands
  - ✅ Automatic command registration
  - ✅ Annotation support
    
    
  ### Debug Ext
    
  A fully featured debug and utilities suite to help you get your bots made
    
  ### Jurigged
    
  A hot reloading extension allowing you to automagically update your bot without reboots
    
  ### Sentry
    
  Integrates Sentry.io error tracking into your bot with a single line

</details>

## Where do I start?

`pip install -U discord-py-interactions`
```python
import interactions

bot = interactions.Client()

@interactions.listen()
async def on_start():
    print("Bot is ready!")
    
bot.start("token")
```

Please check out our [quickstart guide](https://interactionspy.rtfd.io/en/latest/quickstart.html) for
some basic examples.
