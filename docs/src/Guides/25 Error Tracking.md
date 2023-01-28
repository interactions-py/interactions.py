# Error Tracking

So, you've finally got your bot running on a server somewhere.  Chances are, you're not checking the console output 24/7, looking for exceptions.

You're going to want to have some way of tracking if errors occur.

# The simple and dirty method

!!! Please don't actually do this.

The most obvious solution is to think "Well, I'm writing a Discord Bot.  Why not send my errors to a discord channel?"

```python

@listen()
async def on_error(error):
    await bot.get_channel(LOGGING_CHANNEL_ID).send(f"```\n{error.source}\n{error.error}\n```)
```

And this is great when debugging.  But it consumes your rate limit, can run into the 2000 character message limit, and won't work on shards that don't contain your personal server.  It's also very hard to notice patterns and can be noisy.

# So what should I do instead?

NAFF contains built-in support for Sentry.io, a cloud error tracking platform.

To enable it, call `bot.load_extension('naff.ext.sentry', token=SENTRY_TOKEN)` as early as possible in your startup. (Load it before your own extensions, so it can catch intitialization errors in those extensions)

# What does this do that vanilla Sentry doesn't?

We add some [tags](https://docs.sentry.io/platforms/python/enriching-events/tags/) and [contexts](https://docs.sentry.io/platforms/python/enriching-events/context/) that might be useful, and filter out some internal-errors that you probably don't want to see.
