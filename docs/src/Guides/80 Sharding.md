# Sharding

Oh damn, your bot is getting pretty big, huh? Well I guess its time we discuss sharding.

Sharding, in the simplest sense, is splitting up the load on your bot. Discord requires sharding once you reach 2500 guilds, but your bot might be able to handle more than that with a single process.
That's where the [AutoShardedClient](/API Reference/AutoShardClient) comes in.

The AutoShardedClient is a subclass of the [Client](/API Reference/Client) class, and it's basically the same as the Client class, except it's automatically sharding your bot under the hood.
Simply start your bot with this client, and it will automatically shard based on Discord's requests. If you need to, you can also manually specify shards.

How do you use it? Well that's the easy part, lets say this is your code

```python
from naff import Client, listen

class Bot(Client):
    async def on_ready(self):
        print("Ready")
        print(f"This bot is owned by {self.owner}")

    @listen()
    async def on_message_create(self, event):
        print(f"message received: {event.message.content}")
```
To make it sharded we make one change:
```python
from naff import AutoShardedClient, listen

class Bot(AutoShardedClient):
    async def on_ready(self):
        print("Ready")
        print(f"This bot is owned by {self.owner}")

    @listen()
    async def on_message_create(self, event):
        print(f"message received: {event.message.content}")
```
And that's it, your bot is now able to automatically shard.

Sounds pretty cool, huh? So what's the catch? Well, this keeps the bot in a single process, meaning there is no load-balancing.
If your bot is getting large, no matter how many shards you have, it will be slow. That's where splitting the bot into multiple processes is the best solution. But that's outside the scope of this guide 😉.
