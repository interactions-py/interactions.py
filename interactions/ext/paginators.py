import asyncio
import textwrap
import uuid
from typing import Callable, Coroutine, List, Optional, Sequence, TYPE_CHECKING, Union

import attrs

from interactions import (
    Embed,
    ComponentContext,
    ActionRow,
    Button,
    ButtonStyle,
    spread_to_rows,
    ComponentCommand,
    BaseContext,
    Message,
    MISSING,
    Snowflake_Type,
    StringSelectMenu,
    StringSelectOption,
    Color,
    BrandColors,
)
from interactions.client.utils.serializer import export_converter
from interactions.models.discord.emoji import process_emoji, PartialEmoji

if TYPE_CHECKING:
    from interactions import Client
    from interactions.ext.prefixed_commands.context import PrefixedContext

__all__ = ("Paginator",)


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class Timeout:
    paginator: "Paginator" = attrs.field(
        repr=False,
    )
    """The paginator that this timeout is associated with."""
    run: bool = attrs.field(repr=False, default=True)
    """Whether or not this timeout is currently running."""
    ping: asyncio.Event = asyncio.Event()
    """The event that is used to wait the paginator action."""

    async def __call__(self) -> None:
        while self.run:
            try:
                await asyncio.wait_for(self.ping.wait(), timeout=self.paginator.timeout_interval)
            except asyncio.TimeoutError:
                if self.paginator.message:
                    await self.paginator.message.edit(components=self.paginator.create_components(True))
                return
            else:
                self.ping.clear()


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class Page:
    content: str = attrs.field(
        repr=False,
    )
    """The content of the page."""
    title: Optional[str] = attrs.field(repr=False, default=None)
    """The title of the page."""
    prefix: str = attrs.field(repr=False, kw_only=True, default="")
    """Content that is prepended to the page."""
    suffix: str = attrs.field(repr=False, kw_only=True, default="")
    """Content that is appended to the page."""

    @property
    def get_summary(self) -> str:
        """Get the short version of the page content."""
        return self.title or textwrap.shorten(self.content, 40, placeholder="...")

    def to_embed(self) -> Embed:
        """Process the page to an embed."""
        return Embed(description=f"{self.prefix}\n{self.content}\n{self.suffix}", title=self.title)


@attrs.define(eq=False, order=False, hash=False, kw_only=False)
class Paginator:
    client: "Client" = attrs.field(
        repr=False,
    )
    """The client to hook listeners into"""

    page_index: int = attrs.field(repr=False, kw_only=True, default=0)
    """The index of the current page being displayed"""
    pages: Sequence[Page | Embed] = attrs.field(repr=False, factory=list, kw_only=True)
    """The pages this paginator holds"""
    timeout_interval: int = attrs.field(repr=False, default=0, kw_only=True)
    """How long until this paginator disables itself"""
    callback: Callable[..., Coroutine] = attrs.field(repr=False, default=None)
    """A coroutine to call should the select button be pressed"""

    show_first_button: bool = attrs.field(repr=False, default=True)
    """Should a `First` button be shown"""
    show_back_button: bool = attrs.field(repr=False, default=True)
    """Should a `Back` button be shown"""
    show_next_button: bool = attrs.field(repr=False, default=True)
    """Should a `Next` button be shown"""
    show_last_button: bool = attrs.field(repr=False, default=True)
    """Should a `Last` button be shown"""
    show_callback_button: bool = attrs.field(repr=False, default=False)
    """Show a button which will call the `callback`"""
    show_select_menu: bool = attrs.field(repr=False, default=False)
    """Should a select menu be shown for navigation"""

    first_button_emoji: Optional[Union["PartialEmoji", dict, str]] = attrs.field(
        repr=False, default="⏮️", metadata=export_converter(process_emoji)
    )
    """The emoji to use for the first button"""
    back_button_emoji: Optional[Union["PartialEmoji", dict, str]] = attrs.field(
        repr=False, default="⬅️", metadata=export_converter(process_emoji)
    )
    """The emoji to use for the back button"""
    next_button_emoji: Optional[Union["PartialEmoji", dict, str]] = attrs.field(
        repr=False, default="➡️", metadata=export_converter(process_emoji)
    )
    """The emoji to use for the next button"""
    last_button_emoji: Optional[Union["PartialEmoji", dict, str]] = attrs.field(
        repr=False, default="⏩", metadata=export_converter(process_emoji)
    )
    """The emoji to use for the last button"""
    callback_button_emoji: Optional[Union["PartialEmoji", dict, str]] = attrs.field(
        repr=False, default="✅", metadata=export_converter(process_emoji)
    )
    """The emoji to use for the callback button"""

    wrong_user_message: str = attrs.field(repr=False, default="This paginator is not for you")
    """The message to be sent when the wrong user uses this paginator"""

    default_title: Optional[str] = attrs.field(repr=False, default=None)
    """The default title to show on the embeds"""
    default_color: Color = attrs.field(repr=False, default=BrandColors.BLURPLE)
    """The default colour to show on the embeds"""
    default_button_color: Union[ButtonStyle, int] = attrs.field(repr=False, default=ButtonStyle.BLURPLE)
    """The color of the buttons"""

    _uuid: str = attrs.field(repr=False, factory=uuid.uuid4)
    _message: Message = attrs.field(repr=False, default=MISSING)
    _timeout_task: Timeout = attrs.field(repr=False, default=MISSING)
    _author_id: Snowflake_Type = attrs.field(repr=False, default=MISSING)

    def __attrs_post_init__(self) -> None:
        self.client.add_component_callback(
            ComponentCommand(
                name=f"Paginator:{self._uuid}",
                callback=self._on_button,
                listeners=[
                    f"{self._uuid}|select",
                    f"{self._uuid}|first",
                    f"{self._uuid}|back",
                    f"{self._uuid}|callback",
                    f"{self._uuid}|next",
                    f"{self._uuid}|last",
                ],
            )
        )

    @property
    def message(self) -> Message:
        """The message this paginator is currently attached to"""
        return self._message

    @property
    def author_id(self) -> Snowflake_Type:
        """The ID of the author of the message this paginator is currently attached to"""
        return self._author_id

    @classmethod
    def create_from_embeds(cls, client: "Client", *embeds: Embed, timeout: int = 0) -> "Paginator":
        """
        Create a paginator system from a list of embeds.

        Args:
            client: A reference to the client
            *embeds: The embeds to use for each page
            timeout: A timeout to wait before closing the paginator

        Returns:
            A paginator system
        """
        return cls(client, pages=list(embeds), timeout_interval=timeout)

    @classmethod
    def create_from_string(
        cls,
        client: "Client",
        content: str,
        prefix: str = "",
        suffix: str = "",
        page_size: int = 4000,
        timeout: int = 0,
    ) -> "Paginator":
        """
        Create a paginator system from a string.

        Args:
            client: A reference to the client
            content: The content to paginate
            prefix: The prefix for each page to use
            suffix: The suffix for each page to use
            page_size: The maximum characters for each page
            timeout: A timeout to wait before closing the paginator

        Returns:
            A paginator system
        """
        content_pages = textwrap.wrap(
            content,
            width=page_size - (len(prefix) + len(suffix)),
            break_long_words=True,
            break_on_hyphens=False,
            replace_whitespace=False,
        )
        pages = [Page(c, prefix=prefix, suffix=suffix) for c in content_pages]
        return cls(client, pages=pages, timeout_interval=timeout)

    @classmethod
    def create_from_list(
        cls,
        client: "Client",
        content: list[str],
        prefix: str = "",
        suffix: str = "",
        page_size: int = 4000,
        timeout: int = 0,
    ) -> "Paginator":
        """
        Create a paginator from a list of strings. Useful to maintain formatting.

        Args:
            client: A reference to the client
            content: The content to paginate
            prefix: The prefix for each page to use
            suffix: The suffix for each page to use
            page_size: The maximum characters for each page
            timeout: A timeout to wait before closing the paginator

        Returns:
            A paginator system
        """
        pages = []
        page = ""
        for entry in content:
            if len(page) + len(f"\n{entry}") <= page_size:
                page += f"{entry}\n"
            else:
                pages.append(Page(page, prefix=prefix, suffix=suffix))
                page = ""
        if page != "":
            pages.append(Page(page, prefix=prefix, suffix=suffix))
        return cls(client, pages=pages, timeout_interval=timeout)

    def create_components(self, disable: bool = False) -> List[ActionRow]:
        """
        Create the components for the paginator message.

        Args:
            disable: Should all the components be disabled?

        Returns:
            A list of ActionRows

        """
        output = []

        if self.show_select_menu:
            current = self.pages[self.page_index]
            output.append(
                StringSelectMenu(
                    *(
                        StringSelectOption(
                            label=f"{i+1} {p.get_summary if isinstance(p, Page) else p.title}", value=str(i)
                        )
                        for i, p in enumerate(self.pages)
                    ),
                    custom_id=f"{self._uuid}|select",
                    placeholder=f"{self.page_index+1} {current.get_summary if isinstance(current, Page) else current.title}",
                    max_values=1,
                    disabled=disable,
                )
            )

        if self.show_first_button:
            output.append(
                Button(
                    style=self.default_button_color,
                    emoji=PartialEmoji.from_dict(process_emoji(self.first_button_emoji)),
                    custom_id=f"{self._uuid}|first",
                    disabled=disable or self.page_index == 0,
                )
            )
        if self.show_back_button:
            output.append(
                Button(
                    style=self.default_button_color,
                    emoji=PartialEmoji.from_dict(process_emoji(self.back_button_emoji)),
                    custom_id=f"{self._uuid}|back",
                    disabled=disable or self.page_index == 0,
                )
            )

        if self.show_callback_button:
            output.append(
                Button(
                    style=self.default_button_color,
                    emoji=PartialEmoji.from_dict(process_emoji(self.callback_button_emoji)),
                    custom_id=f"{self._uuid}|callback",
                    disabled=disable,
                )
            )

        if self.show_next_button:
            output.append(
                Button(
                    style=self.default_button_color,
                    emoji=PartialEmoji.from_dict(process_emoji(self.next_button_emoji)),
                    custom_id=f"{self._uuid}|next",
                    disabled=disable or self.page_index >= len(self.pages) - 1,
                )
            )
        if self.show_last_button:
            output.append(
                Button(
                    style=self.default_button_color,
                    emoji=PartialEmoji.from_dict(process_emoji(self.last_button_emoji)),
                    custom_id=f"{self._uuid}|last",
                    disabled=disable or self.page_index >= len(self.pages) - 1,
                )
            )

        return spread_to_rows(*output)

    def to_dict(self) -> dict:
        """Convert this paginator into a dictionary for sending."""
        page = self.pages[self.page_index]

        if isinstance(page, Page):
            page = page.to_embed()
            if not page.title and self.default_title:
                page.title = self.default_title
        if not page.footer:
            page.set_footer(f"Page {self.page_index+1}/{len(self.pages)}")
        if not page.color:
            page.color = self.default_color

        return {
            "embeds": [page.to_dict()],
            "components": [c.to_dict() for c in self.create_components()],
        }

    async def send(self, ctx: BaseContext, **kwargs) -> Message:
        """
        Send this paginator.

        Args:
            ctx: The context to send this paginator with
            **kwargs: Additional options to pass to `send`.

        Returns:
            The resulting message

        """
        self._message = await ctx.send(**self.to_dict(), **kwargs)
        self._author_id = ctx.author.id

        if self.timeout_interval > 1:
            self._timeout_task = Timeout(self)
            _ = asyncio.create_task(self._timeout_task())

        return self._message

    async def reply(self, ctx: "PrefixedContext", **kwargs) -> Message:
        """
        Reply this paginator to ctx.

        Args:
            ctx: The context to reply this paginator with
            **kwargs: Additional options to pass to `reply`.

        Returns:
            The resulting message
        """
        self._message = await ctx.reply(**self.to_dict(), **kwargs)
        self._author_id = ctx.author.id

        if self.timeout_interval > 1:
            self._timeout_task = Timeout(self)
            _ = asyncio.create_task(self._timeout_task())

        return self._message

    async def stop(self) -> None:
        """Disable this paginator."""
        if self._timeout_task:
            self._timeout_task.run = False
            self._timeout_task.ping.set()
        await self._message.edit(components=self.create_components(True))

    async def update(self) -> None:
        """
        Update the paginator to the current state.

        Use this if you have programmatically changed the page_index

        """
        await self._message.edit(**self.to_dict())

    async def _on_button(self, ctx: ComponentContext, *args, **kwargs) -> Optional[Message]:
        if ctx.author.id != self.author_id:
            return (
                await ctx.send(self.wrong_user_message, ephemeral=True)
                if self.wrong_user_message
                else await ctx.defer(edit_origin=True)
            )
        if self._timeout_task:
            self._timeout_task.ping.set()
        match ctx.custom_id.split("|")[1]:
            case "first":
                self.page_index = 0
            case "last":
                self.page_index = len(self.pages) - 1
            case "next":
                if (self.page_index + 1) < len(self.pages):
                    self.page_index += 1
            case "back":
                if self.page_index >= 1:
                    self.page_index -= 1
            case "select":
                self.page_index = int(ctx.values[0])
            case "callback":
                if self.callback:
                    return await self.callback(ctx)

        await ctx.edit_origin(**self.to_dict())
        return None


def setup(_) -> None:
    """A dummy setup function to trip the extension loader"""
    raise RuntimeError(
        "`interactions.ext.paginator` should not be loaded as an extension - instead import it and use it in your code."
    )
