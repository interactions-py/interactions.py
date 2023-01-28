# Tasks

Tasks are background processes that can be used to asynchronously run code with a specified trigger.

## How They Work

Tasks work by creating an `asyncio.Task` to run a loop to check if the task is ready to be run based on the provided trigger. Using them is fairly easy, and the easiest way is via **Decorators**.

=== ":one: Decorators"
    Decorators are by far the easier way to run tasks, with very simple syntax to get started.

    ```python
    from naff import Task, IntervalTrigger

    @Task.create(IntervalTrigger(minutes=10)) # (1)!
    async def print_every_ten():
        print("It's been 10 minutes!")
    ```
    { .annotate }

    1. This will create a task that runs every 10 minutes

=== ":two: Manual Registration"
    You can also manually register tasks

    ```python
    from naff import Task, IntervalTrigger

    async def print_every_ten():
        print("It's been 10 minutes!")

    task = Task(print_every_ten, IntervalTrigger(minutes=10))
    ```

By default, there are a few triggers available to the user.

=== ":one: IntervalTrigger"

    These triggers run every set interval.

    ```python
    from naff import Task, IntervalTrigger

    @Task.create(IntervalTrigger(minutes=10))
    async def print_every_ten():
        print("It's been 10 minutes!")
    ```

=== ":two: DateTrigger"

    These triggers are similar to IntervalTriggers, but instead run when a specified datetime is reached.

    ```python
    from datetime import datetime, timedelta
    from naff import Task, DateTrigger

    future = datetime.strptime("%d-%m-%Y", "01-01-2100") # (1)!

    @Task.create(DateTrigger(future)) # (2)!
    async def new_century():
        print("Welcome to the 22nd Century!")
    ```
    { .annotate }

    1. This create a `datetime` object for January 1, 2100
    2. This uses the `future` object to create a `Task` scheduled for January 1, 2100

=== ":three: TimeTrigger"

    These triggers are similar to DateTriggers, but trigger daily at the specified hour, minute, and second.

    ```python
    from naff import Task, TimeTrigger

    @Task.create(TimeTrigger(hour=0, minute=0)) # (1)!
    async def midnight():
        print("It's midnight!")
    ```
    { .annotate }

    1. This creates a task to run at midnight every day

=== ":four: OrTrigger"

    These triggers are special, in that you can pass in a list of different triggers, and if any of them are triggered, it runs the function.

    ```python
    from naff import Task, OrTrigger, TimeTrigger

    @Task.create(OrTrigger(TimeTrigger(hour=5, minute=0), TimeTrigger(hour=17, minute=0)) # (1)!
    async def five():
        print("It's 5 O'clock somewhere, and that somewhere is here!")
    ```
    { .annotate }

    1. This creates a task that triggers at either 5 AM local time or 5 PM local time

## Starting a task

To start a task that has been created, you need to run the `Task.start()` method from an `async` function. A good place to do this is during `on_startup`:
=== ":one: Decorators"

    ```python
    from naff import Client, Intents, Task, IntervalTrigger, listen

    @Task.create(IntervalTrigger(minutes=10))
    async def print_every_ten():
        print("It's been 10 minutes!")

    bot = Client(intents=Intents.DEFAULT)

    @listen()
    async def on_startup(): # (1)!
        await print_every_ten.start()
    ```
    { .annotate }

    1. See [Events](/Guides/10 Events/) for more information

=== ":two: Manual Registration"

    ```python
    from naff import Client, Intents, Task, IntervalTrigger, listen

    async def print_every_ten():
        print("It's been 10 minutes!")

    bot = Client(intents=Intents.DEFAULT)
    task = Task(IntervalTrigger(minutes=10))

    @listen()
    async def on_startup():
        await task.start()
    ```
