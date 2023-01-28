# Live Patching

NAFF has a few built-in extensions that add some features, primarily for debugging. One of these extensions that you can enable separately is to add [`jurigged`](https://github.com/breuleux/jurigged) for live patching of code.

## How to enable

```py
bot.load_extension("naff.ext.jurigged")
```

That's it! The extension will handle all of the leg work, and all you'll notice is that you have more messages in your logs (depending on the log level).

## What is jurigged?

`jurigged` is a library written to allow code hot reloading in Python. It allows you to edit code and have it automagically be updated in your program the next time it is run. The code under the hood is extremely complicated, but the interface to use it is relatively simple.

## How is this useful?

NAFF takes advantage of jurigged to reload any and all commands that were edited whenever a change is made, allowing you to have more uptime with while still adding/improving features of your bot.
