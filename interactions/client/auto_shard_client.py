import asyncio
import time
from collections import defaultdict
from typing import TYPE_CHECKING, Optional

import interactions.api.events as events
from interactions.api.events import ShardConnect
from interactions.api.gateway.state import ConnectionState
from interactions.client.client import Client
from interactions.client.const import MISSING
from interactions.models import (
    Guild,
    to_snowflake,
)
from interactions.models.discord import Status, Activity
from interactions.models.internal.listener import Listener

if TYPE_CHECKING:
    from interactions.models import Snowflake_Type

__all__ = ("AutoShardedClient",)

from ..api.gateway.gateway import GatewayClient


class AutoShardedClient(Client):
    """
    A client to automatically shard the bot.

    You can optionally specify the total number of shards to start with, or it will be determined automatically.
    """

    def __init__(self, *args, **kwargs) -> None:
        self.auto_sharding = "total_shards" not in kwargs
        super().__init__(*args, **kwargs)

        self._connection_state = None

        self._connection_states: list[ConnectionState] = []

        self.max_start_concurrency: int = 1

    @property
    def gateway_started(self) -> bool:
        """Returns if the gateway has been started in all shards."""
        return all(state.gateway_started.is_set() for state in self._connection_states)

    @property
    def shards(self) -> list[ConnectionState]:
        """Returns a list of all shards currently in use."""
        return self._connection_states

    @property
    def latency(self) -> float:
        """The average latency of all active gateways."""
        if len(self._connection_states):
            latencies = sum((g.latency for g in self._connection_states))
            return latencies / len(self._connection_states)
        return float("inf")

    @property
    def latencies(self) -> dict[int, float]:
        """
        Return a dictionary of latencies for all shards.

        Returns:
            {shard_id: latency}
        """
        return {state.shard_id: state.latency for state in self._connection_states}

    async def stop(self) -> None:
        """Shutdown the bot."""
        self.logger.debug("Stopping the bot.")
        self._ready.clear()
        await self.http.close()
        await asyncio.gather(*(state.stop() for state in self._connection_states))

    def get_guild_websocket(self, guild_id: "Snowflake_Type") -> GatewayClient:
        """
        Get the appropriate websocket for a given guild

        Args:
            guild_id: The ID of the guild

        Returns:
            A gateway client for the given ID
        """
        shard_id = (int(guild_id) >> 22) % self.total_shards
        return next((state for state in self._connection_states if state.shard_id == shard_id), MISSING).gateway

    def get_shards_guild(self, shard_id: int) -> list[Guild]:
        """
        Returns the guilds that the specified shard can see

        Args:
            shard_id: The ID of the shard

        Returns:
            A list of guilds
        """
        return [guild for key, guild in self.cache.guild_cache.items() if ((key >> 22) % self.total_shards) == shard_id]

    def get_shard_id(self, guild_id: "Snowflake_Type") -> int:
        """
        Get the shard ID for a given guild.

        Args:
            guild_id: The ID of the guild

        Returns:
            The shard ID for the guild
        """
        return (int(guild_id) >> 22) % self.total_shards

    @Listener.create()
    async def _on_websocket_ready(self, event: events.RawGatewayEvent) -> None:
        """
        Catches websocket ready and determines when to dispatch the client `READY` signal.

        Args:
            event: The websocket ready packet
        """
        connection_data = event.data
        expected_guilds = {to_snowflake(guild["id"]) for guild in connection_data["guilds"]}
        shard_id, total_shards = connection_data["shard"]
        connection_state = next((state for state in self._connection_states if state.shard_id == shard_id), None)

        if expected_guilds:
            while True:
                try:
                    await asyncio.wait_for(self._guild_event.wait(), self.guild_event_timeout)
                except asyncio.TimeoutError:
                    self.logger.warning("Timeout waiting for guilds cache: Not all guilds will be in cache")
                    break
                self._guild_event.clear()
                if all(self.cache.get_guild(g_id) is not None for g_id in expected_guilds):
                    # all guilds cached
                    break

            if self.fetch_members:
                self.logger.info(f"Shard {shard_id} is waiting for members to be chunked")
                await asyncio.gather(*(guild.chunked.wait() for guild in self.guilds if guild.id in expected_guilds))
        else:
            self.logger.warning(
                f"Shard {shard_id} reports it has 0 guilds, this is an indicator you may be using too many shards"
            )
        # noinspection PyProtectedMember
        connection_state._shard_ready.set()
        self.dispatch(ShardConnect(shard_id))
        self.logger.debug(f"Shard {shard_id} is now ready")

        # noinspection PyProtectedMember
        await asyncio.gather(*[shard._shard_ready.wait() for shard in self._connection_states])

        # run any pending startup tasks
        if self.async_startup_tasks:
            try:
                await asyncio.gather(*self.async_startup_tasks)
            except Exception as e:
                self.dispatch(events.Error(source="async-extension-loader", error=e))

        # cache slash commands
        if not self._startup:
            await self._init_interactions()

        if not self._ready.is_set():
            self._ready.set()
            if not self._startup:
                self._startup = True
                self.dispatch(events.Startup())
            self.dispatch(events.Ready())

    async def astart(self, token: str | None = None) -> None:
        """
        Asynchronous method to start the bot.

        Args:
            token: Your bot's token
        """
        self.logger.debug("Starting http client...")
        await self.login(token)

        tasks = []

        # Sort shards into their respective ratelimit buckets
        shard_buckets = defaultdict(list)
        for shard in self._connection_states:
            bucket = str(shard.shard_id % self.max_start_concurrency)
            shard_buckets[bucket].append(shard)

        for bucket in shard_buckets.values():
            for shard in bucket:
                self.logger.debug(f"Starting {shard.shard_id}")
                start = time.perf_counter()
                tasks.append(asyncio.create_task(shard.start()))

                if self.max_start_concurrency == 1:
                    # connection ratelimiting when discord has asked for one connection concurrently
                    # noinspection PyProtectedMember
                    await shard._shard_ready.wait()
                    await asyncio.sleep(5.1 - (time.perf_counter() - start))

            # wait for shards to finish starting
            # noinspection PyProtectedMember
            await asyncio.gather(*[shard._shard_ready.wait() for shard in self._connection_states])

        try:
            await asyncio.gather(*tasks)
        finally:
            await self.stop()

    async def login(self, token: str | None = None) -> None:
        """
        Login to discord via http.

        !!! note
            You will need to run Client.start_gateway() before you start receiving gateway events.

        Args:
            token str: Your bot's token

        """
        await super().login(token)
        data = await self.http.get_gateway_bot()

        self.max_start_concurrency = data["session_start_limit"]["max_concurrency"]
        if self.auto_sharding:
            self.total_shards = data["shards"]
        elif data["shards"] != self.total_shards:
            recommended_shards = data["shards"]
            self.logger.info(
                f"Discord recommends you start with {recommended_shards} shard{'s' if recommended_shards != 1 else ''} instead of {self.total_shards}"
            )

        self.logger.debug(f"Starting bot with {self.total_shards} shard{'s' if self.total_shards != 1 else ''}")
        self._connection_states: list[ConnectionState] = [
            ConnectionState(self, self.intents, shard_id) for shard_id in range(self.total_shards)
        ]

    async def change_presence(
        self,
        status: Optional[str | Status] = Status.ONLINE,
        activity: Optional[str | Activity] = None,
        *,
        shard_id: int | None = None,
    ) -> None:
        """
        Change the bot's presence.

        Args:
            status: The status for the bot to be. i.e. online, afk, etc.
            activity: The activity for the bot to be displayed as doing.
            shard_id: The shard to change the presence on. If not specified, the presence will be changed on all shards.

        !!! note
            Bots may only be `playing` `streaming` `listening` `watching` or `competing`, other activity types are likely to fail.

        """
        if shard_id is None:
            await asyncio.gather(*[shard.change_presence(status, activity) for shard in self._connection_states])
        else:
            await self._connection_states[shard_id].change_presence(status, activity)
