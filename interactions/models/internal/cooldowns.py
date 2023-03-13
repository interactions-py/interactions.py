import asyncio
import time
from enum import IntEnum
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from interactions.models.internal.context import BaseContext

__all__ = ("Buckets", "Cooldown", "CooldownSystem", "MaxConcurrency")


class Buckets(IntEnum):
    """
    Outlines the cooldown buckets that may be used. Should a bucket for guilds exist, and the command is invoked in a DM, a sane default will be used.

    ??? note
         To add your own, override this

    """

    DEFAULT = 0
    """Default is the same as user"""
    USER = 1
    """Per user cooldowns"""
    GUILD = 2
    """Per guild cooldowns"""
    CHANNEL = 3
    """Per channel cooldowns"""
    MEMBER = 4
    """Per guild member cooldowns"""
    CATEGORY = 5
    """Per category cooldowns"""
    ROLE = 6
    """Per role cooldowns"""

    async def get_key(self, context: "BaseContext") -> Any:
        if self is Buckets.USER:
            return context.author.id
        if self is Buckets.GUILD:
            return context.guild_id if context.guild else context.author.id
        if self is Buckets.CHANNEL:
            return context.channel.id
        if self is Buckets.MEMBER:
            return (context.guild_id, context.author.id) if context.guild else context.author.id
        if self is Buckets.CATEGORY:
            return await context.channel.parent_id if context.channel.parent else context.channel.id
        if self is Buckets.ROLE:
            return context.author.top_role.id if context.guild else context.channel.id
        return context.author.id

    def __call__(self, context: "BaseContext") -> Any:
        return self.get_key(context)


class Cooldown:
    """Manages cooldowns and their respective buckets for a command."""

    __slots__ = "bucket", "cooldown_repositories", "rate", "interval"

    def __init__(self, cooldown_bucket: Buckets, rate: int, interval: float) -> None:
        self.bucket: Buckets = cooldown_bucket
        self.cooldown_repositories = {}
        self.rate: int = rate
        self.interval: float = interval

    async def get_cooldown(self, context: "BaseContext") -> "CooldownSystem":
        key = await self.bucket(context)

        if key not in self.cooldown_repositories:
            cooldown = CooldownSystem(self.rate, self.interval)
            self.cooldown_repositories[key] = cooldown
            return cooldown
        return self.cooldown_repositories.get(await self.bucket(context))

    async def acquire_token(self, context: "BaseContext") -> bool:
        """
        Attempt to acquire a token for a command to run. Uses the context of the command to use the correct CooldownSystem.

        Args:
            context: The context of the command

        Returns:
            True if a token was acquired, False if not

        """
        cooldown = await self.get_cooldown(context)

        return cooldown.acquire_token()

    async def get_cooldown_time(self, context: "BaseContext") -> float:
        """
        Get the remaining cooldown time.

        Args:
            context: The context of the command

        Returns:
            remaining cooldown time, will return 0 if the cooldown has not been reached

        """
        cooldown = await self.get_cooldown(context)
        return cooldown.get_cooldown_time()

    async def on_cooldown(self, context: "BaseContext") -> bool:
        """
        Returns the cooldown state of the command.

        Args:
            context: The context of the command

        Returns:
            boolean state if the command is on cooldown or not

        """
        cooldown = await self.get_cooldown(context)
        return cooldown.on_cooldown()

    async def reset_all(self) -> None:
        """
        Resets this cooldown system to its initial state.

        !!! warning     To be clear, this will reset **all** cooldowns
        for this command to their initial states

        """
        # this doesnt need to be async, but for consistency, it is
        self.cooldown_repositories = {}

    async def reset(self, context: "BaseContext") -> None:
        """
        Resets the cooldown for the bucket of which invoked this command.

        Args:
            context: The context of the command

        """
        cooldown = await self.get_cooldown(context)
        cooldown.reset()


class CooldownSystem:
    """
    Represents a cooldown system for commands.

    Attributes:
        rate: How many commands may be ran per interval
        interval: How many seconds to wait for a cooldown
        opened: When this cooldown session began

    """

    __slots__ = "rate", "interval", "opened", "_tokens"

    def __init__(self, rate: int, interval: float) -> None:
        self.rate: int = rate
        self.interval: float = interval
        self.opened: float = 0.0

        self._tokens: int = self.rate

        # sanity checks
        if self.rate == 0:
            raise ValueError("Cooldown rate must be greater than 0")
        if self.interval == 0:
            raise ValueError("Cooldown interval must be greater than 0")

    def reset(self) -> None:
        """Resets the tokens for this cooldown."""
        self._tokens = self.rate
        self.opened = 0.0

    def on_cooldown(self) -> bool:
        """
        Returns the cooldown state of the command.

        Returns:
            boolean state if the command is on cooldown or not
        """
        self.determine_cooldown()

        if self._tokens == 0:
            return True
        return False

    def acquire_token(self) -> bool:
        """
        Attempt to acquire a token for a command to run.

        Returns:
            True if a token was acquired, False if not

        """
        self.determine_cooldown()

        if self._tokens == 0:
            return False
        if self._tokens == self.rate:
            self.opened = time.time()
        self._tokens -= 1

        return True

    def get_cooldown_time(self) -> float:
        """
        Returns how long until the cooldown will reset.

        Returns:
            remaining cooldown time, will return 0 if the cooldown has not been reached

        """
        self.determine_cooldown()
        if self._tokens != 0:
            return 0
        return self.interval - (time.time() - self.opened)

    def determine_cooldown(self) -> None:
        """Determines the state of the cooldown system."""
        c_time = time.time()

        if c_time > self.opened + self.interval:
            # cooldown has expired, reset the cooldown
            self.reset()


class MaxConcurrency:
    """
    Limits how many instances of a command may be running concurrently.

    Attributes:
        bucket Buckets: The bucket this concurrency applies to
        concurrent int: The maximum number of concurrent instances permitted to
        wait bool: Should we wait until a instance is available

    """

    def __init__(self, concurrent: int, concurrency_bucket: Buckets, wait: bool = False) -> None:
        self.bucket: Buckets = concurrency_bucket
        self.concurrency_repository: Dict = {}
        self.concurrent: int = concurrent
        self.wait = wait

    async def get_semaphore(self, context: "BaseContext") -> asyncio.Semaphore:
        """
        Get the semaphore associated with the given context.

        Args:
            context: The commands context

        Returns:
            A semaphore object
        """
        key = await self.bucket(context)

        if key not in self.concurrency_repository:
            semaphore = asyncio.Semaphore(self.concurrent)
            self.concurrency_repository[key] = semaphore
            return semaphore
        return self.concurrency_repository.get(key)

    async def acquire(self, context: "BaseContext") -> bool:
        """
        Acquire an instance of the semaphore.

        Args:
            context:The context of the command
        Returns:
            If the semaphore was successfully acquired

        """
        semaphore = await self.get_semaphore(context)

        if not self.wait and semaphore.locked():
            return False
        acquired = await semaphore.acquire()
        return acquired

    async def release(self, context: "BaseContext") -> None:
        """
        Release the semaphore.

        Args:
            context: The context of the command

        """
        semaphore = await self.get_semaphore(context)

        semaphore.release()
