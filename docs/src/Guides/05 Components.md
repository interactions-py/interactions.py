# Components

While interactions are cool and all, they are still missing a vital component.
Introducing components, aka Buttons, Selects, soon Text Input Fields.
Components can be added to any message by passing them to `components` in any `.send()` method.

They are organised in a 5x5 grid, so you either have to manage the layout yourself, use `spread_to_rows()` where we organise them for you, or have a single component.

If you want to define the layout yourself, you have to put them in an `ActionRow()`. The `components` parameter need a list of up to five `ActionRow()`.

=== ":one: `ActionRow()`"
    ```python
    components: list[ActionRow] = [
        ActionRow(
            Button(
                style=ButtonStyles.GREEN,
                label="Click Me",
            ),
            Button(
                style=ButtonStyles.GREEN,
                label="Click Me Too",
            )
        )
    ]

    await channel.send("Look, Buttons!", components=components)
    ```

=== ":two: `spread_to_rows()`"
    ```python
    components: list[ActionRow] = spread_to_rows(
        Button(
            style=ButtonStyles.GREEN,
            label="Click Me",
        ),
        Button(
            style=ButtonStyles.GREEN,
            label="Click Me Too",
        )
    )

    await channel.send("Look, Buttons!", components=components)
    ```

=== ":three: With only one component"
    If you only have **one** component, you do not need to worry about the layout at all and can simply pass it.
    We will put it in an `ActionRow` behind the scenes.

    ```python
    components = Button(
        style=ButtonStyles.GREEN,
        label="Click Me",
    )

    await channel.send("Look, Buttons!", components=components)
    ```

For simplicity's sake, example three will be used for all examples going forward.

If you want to delete components, you need to pass `components=[]` to `.edit()`.

## You Have To Button Up

Buttons are, you guessed right, buttons. Users can click them, and they can be disabled if you wish. That's all really.

```python
components = Button(
    style=ButtonStyles.GREEN,
    label="Click Me",
    disabled=False,
)

await channel.send("Look a Button!", components=components)
```

For more information, please visit the API reference [here](/API Reference/models/Discord/components/#naff.models.discord.components.Button).

### I Need More Style

You are in luck, there are a bunch of colours you can choose from.
    <br>![Button Colours](../images/Components/buttons.png "Button Colours")

The colours correspond to the styles found in `ButtonStyles`. Click [here](/API Reference/models/Discord/enums/#naff.models.discord.enums.ButtonStyles) for more information.

If you use `ButtonStyles.URL`, you can pass an url to the button with `url`. Users who click the button will get redirected to your url.
```python
components = Button(
    style=ButtonStyles.URL,
    label="Click Me",
    url="https://github.com/Discord-Snake-Pit/NAFF",
)

await channel.send("Look a Button!", components=components)
```

`ButtonStyles.URL` does not receive events, or work with callbacks.

## Select Your Favorite

Sometimes there might be more than a handful options which users need to decide between. That's when a `Select` should probably be used.

Selects are very similar to Buttons. The main difference is that you get a list of options to choose from.

If you want to use string options, then you use `StringSelect`. Simply pass a list of strings to `options` and you are good to go. You can also explicitly pass `SelectOptions` to control the value attribute.

You can also define how many options users can choose by setting `min_values` and `max_values`.

```python
from naff import StringSelectMenu, SelectOption

components = StringSelectMenu(
    options=[
        "Pizza", "Pasta", "Burger", "Salad"
    ],
    placeholder="What is your favourite food?",
    min_values=1,
    max_values=1,
)

await channel.send("Look a Select!", components=components)
```
    ??? note
        You can only have upto 25 options in a Select

Alternatively, you can use `RoleSelectMenu`, `UserSelectMenu` and `ChannelSelectMenu` to select roles, users and channels respectively. These select menus are very similar to `StringSelectMenu`, but they don't allow you to pass a list of options; it's all done behind the scenes.

```python

For more information, please visit the API reference [here](/API Reference/models/Discord/components/#naff.models.discord.components.Select).

## Responding

Okay now you can make components, but how do you interact with users?
There are three ways to respond to components.

If you add your component to a temporary message asking for additional user input, just should probably use `bot.wait_for_component()`.
These have the downside that, for example, they won't work anymore after restarting your bot.

Otherwise, you are looking for a persistent callback. For that, you want to define `custom_id` in your component creation.

When responding to a component you need to satisfy discord either by responding to the context with `ctx.send()` or by editing the component with `ctx.edit_origin()`. You get access to the context with `component.context`.

=== ":one: `bot.wait_for_component()`"
    As with discord.py, this supports checks and timeouts.

    In this example, we are checking that the username starts with "a" and clicks the button within 30 seconds.
    If it times out, we're just gonna disable it
    ```python
    components = Button(
        custom_id="my_button_id",
        style=ButtonStyles.GREEN,
        label="Click Me",
    )

    message = await channel.send("Look a Button!", components=components)

    # define the check
    def check(component: Button) -> bool:
        return component.context.author.startswith("a")

    try:
        # you need to pass the component you want to listen for here
        # you can also pass an ActionRow, or a list of ActionRows. Then a press on any component in there will be listened for
        used_component = await bot.wait_for_component(components=components, check=check, timeout=30)

    except TimeoutError:  
        print("Timed Out!")

        components[0].components[0].disabled = True
        await message.edit(components=components)

    else:
        await used_component.context.send("Your name starts with 'a'")
    ```

    You can also use this to check for a normal message instead of a component interaction.

    For more information, please visit the API reference [here](/API Reference/client/).


=== ":two: Persistent Callback Option 1"
    You can listen to the `on_component()` event and then handle your callback. This works even after restarts!

    ```python
    async def my_command(...):
        components = Button(
            custom_id="my_button_id",
            style=ButtonStyles.GREEN,
            label="Click Me",
        )

        await channel.send("Look a Button!", components=components)

    @listen()
    async def on_component(event: Component):
        ctx = event.context

        match ctx.custom_id:
            case "my_button_id":
                await ctx.send("You clicked it!")
    ```

=== ":two: Persistent Callback Option 2"
    If you have a lot of components, putting everything in the `on_component()` event can get messy really quick.

    Similarly to Option 1, you can define `@component_callback` listeners. This works after restarts too.

    You have to pass your `custom_id` to `@component_callback(custom_id)` for the library to be able to register the callback function to the wanted component.

    ```python
    async def my_command(...):
        components = Button(
            custom_id="my_button_id",
            style=ButtonStyles.GREEN,
            label="Click Me",
        )

        await channel.send("Look a Button!", components=components)

    # you need to pass your custom_id to this decorator
    @component_callback("my_button_id")
    async def my_callback(ctx: ComponentContext):
        await ctx.send("You clicked it!")
    ```

=== ":three: Persistent Callback Option 3"
    Personally, I put my callbacks into different files, which is why I use this method, because the usage of different files can make using decorators challenging.

    For this example to work, the function name needs to be the same as the `custom_id` of the component.

    ```python
    async def my_command(...):
        components = Button(
            custom_id="my_button_id",
            style=ButtonStyles.GREEN,
            label="Click Me",
        )

        await channel.send("Look a Button!", components=components)

    # my callbacks go in here or I subclass this if I want to split it up
    class MyComponentCallbacks:
        @staticmethod
        async def my_button_id(ctx: ComponentContext):
            await ctx.send("You clicked it!")

    # magically register all functions from the class
    for custom_id in [k for k in MyComponentCallbacks.__dict__ if not k.startswith("__")]:
        bot.add_component_callback(
            ComponentCommand(
                name=f"ComponentCallback::{custom_id}",
                callback=getattr(ComponentCallbacks, custom_id),
                listeners=[custom_id],
            )
        )
    ```
