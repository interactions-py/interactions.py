# This code shows a very brief and small example of how to create a bot with our library.
# This example does not cover all the features of the library, but it is enough to get you started.
# In order to learn more about how to use the library, please head over to our documentation:
# https://interactionspy.rtfd.io/en/latest/

# The first thing you need to do is import the library.
import interactions

# Now, let's create an instance of a bot.
# When you make a bot, we refer to it as the "client."
# The client is the main object that interacts with the Gateway, what talks to Discord.
# The client is also the main object that interacts with the API, what makes requests with Discord.
client = interactions.Client("your bot token will go here.")

# With our client established, let's have the library inform us when the client is ready.
# These are known as event listeners. An event listener can be established in one of two ways.
# You can provide the name of the event, prefixed by an "on_", by naming the function afterwards
# as the event you want to listen to.
@client.event
async def on_ready():
    # We can use the client "me" attribute to get information about the bot.
    print(f"We're online! We've logged in as {client.me.name}.")

    # We're also able to use property methods to gather additional data.
    print(f"Our latency is {round(client.latency)} ms.")


@client.event
async def on_message_create(message: interactions.Message):
    # Whenever we specify any other event type that isn't "READY," the function underneath
    # the decorator will most likely have an argument required. This argument is the data
    # that is being supplied back to us developers, which we call a data model.

    # In this example, we're listening to messages being created. This means we can expect
    # a "message" argument to be passed to the function, which will be the data model of such.

    # We can use the data model to access the data we need.
    # Keep in mind that you can only access the message content if your bot has the MESSAGE_CONTENT intent.
    # You can find more information on this in the migration section of the quickstart guide.
    print(
        f"We've received a message from {message.author.username}. The message is: {message.content}."
    )


# Now, let's create a command.
# A command is a function that is called when a user types out a command.
# The command is called with a context object, which contains information about the user, the channel, and the guild.
# Context is what we call the described information given from an interaction response, what comes from a command.
# The context object in this case is a class for commands, but can also be one for components if used that way.
@client.command(name="hello-world", description='A command that says "hello world!"')
async def hello_world(ctx: interactions.CommandContext):
    # "ctx" is an abbreviation of the context object.
    # You don't need to type hint this, but it's recommended to do so.

    # Now, let's send back a response.
    # The interaction response should be the LAST thing you do when a command is ran.
    await ctx.send("hello world!")

    # However, any code you put after a response will still execute unless you prevent it from doing so.
    print("we ran.")


# After we've declared all of the bot code we want, we need to tell the library to run our bot.
# In this example, we've decided to do some things in a different way without explicitly saying it:

# - we'll be syncing the commands automatically.
#   if you want to do this manually, you can do it by passing disable_sync=False in the Client
#   object on line 8.
# - we are not setting a presence.
# - we are not automatically sharding, and registering the connection under 1 shard.
# - we are using default intents, which are Gateway intents excluding privileged ones.
client.start()
