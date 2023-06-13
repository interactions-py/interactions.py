import asyncio
import inspect
from asyncio import Task as _Task
from datetime import datetime, timedelta
from typing import Callable

import interactions
from interactions.client.const import get_logger
from .triggers import BaseTrigger

__all__ = ("Task",)


class Task:
    """
    Create an asynchronous background tasks. Tasks allow you to run code according to a trigger object.

    A task's trigger must inherit from `BaseTrigger`.

    Attributes:
        callback (Callable): The function to be called when the trigger is triggered.
        trigger (BaseTrigger): The trigger object that determines when the task should run.
        task (Optional[_Task]): The task object that is running the trigger loop.
        iteration (int): The number of times the task has run.

    """

    callback: Callable
    trigger: BaseTrigger
    task: _Task | None
    _stop: asyncio.Event
    iteration: int

    def __init__(self, callback: Callable, trigger: BaseTrigger) -> None:
        self.callback = callback
        self.trigger = trigger
        self._stop = asyncio.Event()
        self.task = None
        self.iteration = 0

    @property
    def started(self) -> bool:
        """Whether the task is started"""
        return self.task is not None

    @property
    def running(self) -> bool:
        """Whether the task is running"""
        return self.task is not None and not self.task.done()

    @property
    def done(self) -> bool:
        """Whether the task is done/finished"""
        return self.task is not None and self.task.done()

    @property
    def next_run(self) -> datetime | None:
        """Get the next datetime this task will run."""
        return self.trigger.next_fire() if self.running else None

    @property
    def delta_until_run(self) -> timedelta | None:
        """Get the time until the next run of this task."""
        if not self.running:
            return None

        next_run = self.next_run
        return next_run - datetime.now() if next_run is not None else None

    def on_error_sentry_hook(self, error: Exception) -> None:
        """A dummy method for interactions.ext.sentry to hook"""

    def on_error(self, error: Exception) -> None:
        """Error handler for this task. Called when an exception is raised during execution of the task."""
        self.on_error_sentry_hook(error)
        interactions.Client.default_error_handler("Task", error)

    async def __call__(self) -> None:
        try:
            if inspect.iscoroutinefunction(self.callback):
                val = await self.callback()
            else:
                val = self.callback()

            if isinstance(val, BaseTrigger):
                self.reschedule(val)
        except Exception as e:
            self.on_error(e)

    def _fire(self, fire_time: datetime) -> None:
        """Called when the task is being fired."""
        self.trigger.set_last_call_time(fire_time)
        _ = asyncio.create_task(self())
        self.iteration += 1

    async def _task_loop(self) -> None:
        """The main task loop to fire the task at the specified time based on triggers configured."""
        while not self._stop.is_set():
            fire_time = self.trigger.next_fire()
            if fire_time is None:
                return self.stop()

            future = asyncio.create_task(self._stop.wait())
            timeout = (fire_time - datetime.now()).total_seconds()
            done, _ = await asyncio.wait([future], timeout=timeout, return_when=asyncio.FIRST_COMPLETED)
            if future in done:
                return None

            self._fire(fire_time)

    def start(self) -> None:
        """Start this task."""
        try:
            self.trigger.reschedule()
            self._stop.clear()
            self.task = asyncio.create_task(self._task_loop())
        except RuntimeError:
            get_logger().error(
                "Unable to start task without a running event loop! We recommend starting tasks within an `on_startup` event."
            )

    def stop(self) -> None:
        """End this task."""
        self._stop.set()
        if self.task:
            self.task.cancel()

    def restart(self) -> None:
        """Restart this task."""
        self.stop()
        self.start()

    def reschedule(self, trigger: BaseTrigger) -> None:
        """
        Change the trigger being used by this task.

        Args:
            trigger: The new Trigger to use

        """
        self.trigger = trigger
        self.restart()

    @classmethod
    def create(cls, trigger: BaseTrigger) -> Callable[[Callable], "Task"]:
        """
        A decorator to create a task.

        Example:
            ```python
            @Task.create(IntervalTrigger(minutes=5))
            async def my_task():
                print("It's been 5 minutes!")

            @listen()
            async def on_startup():
                my_task.start()
            ```

        Args:
            trigger: The trigger to use for this task

        """

        def wrapper(func: Callable) -> "Task":
            return cls(func, trigger)

        return wrapper
