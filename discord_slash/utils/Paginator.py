import random

from discord.ext.commands import bot

from discord_slash import SlashContext
from discord_slash.context import ComponentContext
from discord_slash.utils.manage_components import (
    create_actionrow,
    create_button,
    wait_for_component,
)


async def Paginator(
    bot: bot,
    ctx: SlashContext,
    pages: list,
    content: str = "",
):
    top = len(pages)  # limit of the paginator
    bid = random.randint(10000, 99999)  # base of button id
    index = 0  # starting page
    controlButtons = [
        create_button(style=3, label="Previous", custom_id=f"{bid}-prev", disabled=True),
        create_button(
            style=1,
            label=f"Page {index+1}/{top}",
            disabled=True,
            custom_id=f"{bid}-index",
        ),
        create_button(style=3, label="Next", custom_id=f"{bid}-next", disabled=False),
    ]
    controls = create_actionrow(*controlButtons)
    await ctx.send(f"{content}", embed=pages[0], components=[controls])
    while True:
        # handling the interaction
        button_context: ComponentContext = await wait_for_component(bot, components=[controls])
        await button_context.defer(edit_origin=True)
        # Handling previous button
        if button_context.component_id == f"{bid}-prev" and index > 0:
            index = index - 1  # lowers index by 1
            if index == 0:
                controls["components"][0]["disabled"] = True  # Disables the previous button
            controls["components"][2]["disabled"] = False  # Enables Next Button
            controls["components"][1]["label"] = f"Page {index+1}/{top}"  # updates the index
            await button_context.edit_origin(
                content=f"{content}", embed=pages[index], components=[controls]
            )
        # handling next button
        if button_context.component_id == f"{bid}-next" and index < top - 1:

            index = index + 1  # add 1 to the index
            if index == top - 1:
                controls["components"][2]["disabled"] = True  # disables the next button
            controls["components"][0]["disabled"] = False  # enables previous button

            controls["components"][1]["label"] = f"Page {index+1}/{top}"  # updates the index
            await button_context.edit_origin(
                content=f"{content}", embed=pages[index], components=[controls]
            )
