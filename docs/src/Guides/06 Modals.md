---
search:
  boost: 3
---

# Modals

Modals are basically popups which a user can use to send text information to your bot. As of the writing of this guide, you can use two components in a modal:

- Short Text Input (single-line)
- Paragraph Text Input (multi-line)

Each component that you define in your modal must have its own `custom_id` so that you can easily retrieve the data that a user sent later.


## Creating a Modal

Modals are one of the ways you can respond to interactions. They are intended for when you need to query a lot of information from a user.

Modals are valid responses to Slash Commands and Components.
You **cannot** respond to a modal with a modal.
Use `ctx.send_modal()` to send a modal.

```python
from interactions import Modal, ParagraphText, ShortText, SlashContext, slash_command

@slash_command(name="my_modal_command", description="Playing with Modals")
async def my_command_function(ctx: SlashContext):
    my_modal = Modal(
        ShortText(label="Short Input Text", custom_id="short_text"),
        ParagraphText(label="Long Input Text", custom_id="long_text"),
        title="My Modal",
    )
    await ctx.send_modal(modal=my_modal)
```

This example leads to the following modal:
    <br>![example_modal.png](../images/Modals/modal_example.png "The Add bot button and text")

### Text Inputs Customisation

Modal components are customisable in their appearance. You can set a placeholder, pre-fill them, restrict what users can input, or make them optional.

```python
from interactions import Modal, ShortText, SlashContext, slash_command

@slash_command(name="my_modal_command", description="Playing with Modals")
async def my_command_function(ctx: SlashContext):
    my_modal = Modal(
        ShortText(
            label="Short Input Text",
            custom_id="short_text",
            value="Pre-filled text",
            min_length=10,
        ),
        ShortText(
            label="Short Input Text",
            custom_id="optional_short_text",
            required=False,
            placeholder="Please be concise",
            max_length=10,
        ),
        title="My Modal",
    )
    await ctx.send_modal(modal=my_modal)
```

This example leads to the following modal:
    <br>![example_modal.png](../images/Modals/modal_example_customisiblity.png "The Add bot button and text")

## Responding

Now that users have input some information, the bot needs to process it and answer back the user. Similarly to the Components guide, there is a persistent and non-persistent way to listen to a modal answer.

The data that the user has input can be found in `ctx.responses`, which is a dictionary with the keys being the custom IDs of your text inputs and the values being the answers the user has entered.

=== ":one: `@bot.wait_for_modal()`"
    As with `bot.wait_for_component()`, `bot.wait_for_modal()` supports timeouts. However, checks are not supported, since modals are not persistent like Components, and only visible to the interaction invoker.

    ```python
    from interactions import Modal, ModalContext, ParagraphText, ShortText, SlashContext, slash_command

    @slash_command(name="test")
    async def command(ctx: SlashContext):
        my_modal = Modal(
            ShortText(label="Short Input Text", custom_id="short_text"),
            ParagraphText(label="Long Input Text", custom_id="long_text"),
            title="My Modal",
            custom_id="my_modal",
        )
        await ctx.send_modal(modal=my_modal)
        modal_ctx: ModalContext = await ctx.bot.wait_for_modal(my_modal)

        # extract the answers from the responses dictionary
        short_text = modal_ctx.responses["short_text"]
        long_text = modal_ctx.responses["long_text"]

        await modal_ctx.send(f"Short text: {short_text}, Paragraph text: {long_text}", ephemeral=True)
    ```

    !!!warning
        In this example, make sure to not mix the two Contexts `ctx` and `modal_ctx`! If the last line of the code is replaced by `ctx.send()`, the text would not be sent because you have already answered the `ctx` variable previously, when sending the modal (`ctx.send_modal()`).

=== ":two: Persistent Callback: `@modal_callback()`"
    In the case of a persistent callback, your callback function must have the names of the custom IDs of your text inputs as its arguments, similar to how you define a callback for a slash command.

    ```python
    from interactions import Modal, ModalContext, ParagraphText, ShortText, SlashContext, modal_callback, slash_command

    @slash_command(name="test")
    async def command(ctx: SlashContext):
        my_modal = Modal(
            ShortText(label="Short Input Text", custom_id="short_text"),
            ParagraphText(label="Long Input Text", custom_id="long_text"),
            title="My Modal",
            custom_id="my_modal",
        )
        await ctx.send_modal(modal=my_modal)

    @modal_callback("my_modal")
    async def on_modal_answer(ctx: ModalContext, short_text: str, long_text: str):
        await ctx.send(f"Short text: {short_text}, Paragraph text: {long_text}", ephemeral=True)
    ```
