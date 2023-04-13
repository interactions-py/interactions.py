import asyncio
import logging
import os
from asyncio import AbstractEventLoop
from contextlib import suppress
from datetime import datetime

import pytest
import pytest_asyncio

import interactions
from interactions import (
    GuildChannel,
    MessageableMixin,
    GuildNews,
    ThreadableMixin,
    ExplicitContentFilterLevel,
    VerificationLevel,
    Client,
    Guild,
    GuildText,
    Embed,
    PartialEmoji,
    BrandColors,
    Permissions,
    Status,
    EmbedField,
    EmbedAuthor,
    EmbedAttachment,
    EmbedFooter,
    StringSelectOption,
    Modal,
    ParagraphText,
    Message,
    GuildVoice,
)
from interactions.models.discord.asset import Asset
from interactions.models.discord.components import ActionRow, Button, StringSelectMenu
from interactions.models.discord.emoji import process_emoji_req_format
from interactions.api.gateway.websocket import WebsocketClient
from interactions.api.http.route import Route
from interactions.api.voice.audio import AudioVolume
from interactions.client.errors import NotFound
from interactions.models.discord.enums import ButtonStyle
from interactions.models.discord.role import Role

__all__ = ()


try:
    import dotenv

    dotenv.load_dotenv()
except ImportError:
    pass

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    pytest.skip(f"Skipping {os.path.basename(__file__)} - no token provided", allow_module_level=True)
if os.environ.get("GITHUB_ACTIONS") and not os.environ.get("RUN_TESTBOT"):
    pytest.skip(f"Skipping {os.path.basename(__file__)} - RUN_TESTBOT not set", allow_module_level=True)

log = logging.getLogger("Interations-Integration-Tests")


@pytest.fixture(scope="module")
def event_loop() -> AbstractEventLoop:
    return asyncio.get_event_loop()


@pytest_asyncio.fixture(scope="module")
async def bot(github_commit) -> Client:
    bot = interactions.Client(activity="Testing someones code")
    await bot.login(TOKEN)
    gw = asyncio.create_task(bot.start_gateway())

    await bot._ready.wait()
    bot.suffix = github_commit
    log.info(f"Logged in as {bot.user} ({bot.user.id}) -- {bot.suffix}")

    yield bot
    gw.cancel()
    with suppress(asyncio.CancelledError):
        await gw


@pytest_asyncio.fixture(scope="module")
async def guild(bot: Client) -> Guild:
    guild = next((g for g in bot.guilds if g.name in ["Interactions.py Test Suite", "NAFF Test Suite"]), None)
    if not guild:
        log.info("No guild found, creating one...")

        guild: interactions.Guild = await interactions.Guild.create("Interactions.py Test Suite", bot)
        community_channel = await guild.create_text_channel("community_channel")

        await guild.edit(
            features=["COMMUNITY"],
            rules_channel=community_channel,
            system_channel=community_channel,
            public_updates_channel=community_channel,
            explicit_content_filter=ExplicitContentFilterLevel.ALL_MEMBERS,
            verification_level=VerificationLevel.LOW,
        )

    yield guild


@pytest_asyncio.fixture(scope="module")
async def channel(bot, guild) -> GuildText:
    channel = await guild.create_text_channel(f"test_scene - {bot.suffix}")
    yield channel
    await channel.delete()


@pytest_asyncio.fixture(scope="module")
async def github_commit() -> str:
    import subprocess

    return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode("ascii").strip()


def ensure_attributes(target_object) -> None:
    for attr in dir(target_object):
        # ensure all props and attributes load correctly
        getattr(target_object, attr)


@pytest.mark.asyncio
async def test_channels(bot: Client, guild: Guild) -> None:
    channels = [
        guild_category := await guild.create_category("_test_category"),
        await guild.create_text_channel(f"_test_text-{bot.suffix}"),
        await guild.create_news_channel(f"_test_news-{bot.suffix}"),
        await guild.create_stage_channel(f"_test_stage-{bot.suffix}"),
        await guild.create_voice_channel(f"_test_voice-{bot.suffix}"),
    ]

    assert all(c in guild.channels for c in channels)

    channels.append(await bot.owner.fetch_dm())

    try:
        for channel in channels:
            ensure_attributes(channel)

            if isinstance(channel, GuildChannel) and channel != guild_category:
                await channel.edit(parent_id=guild_category.id)
                assert channel.category == guild_category

            if isinstance(channel, MessageableMixin) and not isinstance(channel, GuildVoice):
                _m = await channel.send("test")
                assert _m.channel == channel

                if isinstance(channel, GuildNews):
                    await _m.publish()

                await _m.delete()

            if isinstance(channel, ThreadableMixin):
                if isinstance(channel, GuildNews):
                    _tm = await channel.send("dummy message")
                    thread = await _tm.create_thread("new thread")
                else:
                    thread = await channel.create_thread("new thread")
                assert thread.parent_channel == channel
                _m = await thread.send("test")
                assert _m.channel == thread

                _m = await channel.send("start thread here")
                m_thread = await channel.create_thread("new message thread", message=_m)
                assert _m.id == m_thread.id

                assert m_thread in guild.threads
                assert thread in guild.threads
                await thread.delete()
                # We suppress bcu sometimes event fires too fast, before wait_for is called
                with suppress(asyncio.exceptions.TimeoutError):
                    await bot.wait_for("thread_delete", timeout=2)
                assert thread not in guild.threads
    finally:
        for channel in channels:
            with suppress(NotFound):
                await channel.delete()


@pytest.mark.asyncio
async def test_messages(bot: Client, guild: Guild, channel: GuildText) -> None:
    msg = await channel.send("Message Tests")
    thread = await msg.create_thread("Test Thread")

    try:
        _m = await thread.send("Test")
        ensure_attributes(_m)

        await _m.edit(content="Test Edit")
        assert _m.content == "Test Edit"
        await _m.add_reaction("❌")
        with suppress(asyncio.exceptions.TimeoutError):
            await bot.wait_for("message_reaction_add", timeout=2)

        assert len(_m.reactions) == 1

        assert len(await _m.fetch_reaction("❌")) != 0
        await _m.remove_reaction("❌")
        with suppress(asyncio.exceptions.TimeoutError):
            await bot.wait_for("message_reaction_remove", timeout=2)

        await _m.add_reaction("❌")
        await _m.clear_all_reactions()
        with suppress(asyncio.exceptions.TimeoutError):
            await bot.wait_for("message_reaction_remove_all", timeout=2)

        assert len(_m.reactions) == 0

        await _m.pin()
        assert _m.pinned is True
        await _m.suppress_embeds()
        await _m.unpin()

        _r = await _m.reply(f"test-reply {bot.user.mention} {channel.mention}")
        assert _r._referenced_message_id == _m.id

        mem_mentions = []
        async for member in _r.mention_users:
            mem_mentions.append(member)
        assert len(mem_mentions) == 1

        assert len(_r.mention_channels) == 1

        await thread.send(file=r"tests/LordOfPolls.png")

        assert _m.jump_url is not None
        assert _m.proto_url is not None

        await thread.send(embeds=Embed("Test"))

        await thread.delete()

        _m = await bot.owner.send("Test Message from TestSuite")
        await _m.delete()

    finally:
        with suppress(interactions.errors.NotFound):
            await thread.delete()


@pytest.mark.asyncio
async def test_roles(bot: Client, guild: Guild) -> None:
    roles: list[Role] = []

    try:
        with suppress(interactions.errors.Forbidden):
            roles.append(await guild.create_role("_test_role3"))
            # will fail if the test server has not enabled the feature
            roles.append(await guild.create_role("_test_role1", icon="💥"))
            roles.append(await guild.create_role("_test_role2", icon=r"tests/LordOfPolls.png"))

        assert roles[0].icon is None
        with suppress(IndexError):
            assert isinstance(roles[1].icon, PartialEmoji)
            assert isinstance(roles[2].icon, Asset)
        await guild.me.remove_role(roles[0])

        await roles[0].edit(name="_test_renamed", color=BrandColors.RED)

        assert roles[0].name == "_test_renamed"

        for role in roles:
            await role.delete()

    finally:
        for role in guild.roles:
            if role.name.startswith("_test"):
                with suppress(NotFound):
                    await role.delete()


@pytest.mark.asyncio
async def test_members(bot: Client, guild: Guild, channel: GuildText) -> None:
    member = guild.me
    ensure_attributes(member)

    await member.edit_nickname("Test Nickname")
    with suppress(asyncio.exceptions.TimeoutError):
        await bot.wait_for("member_update", timeout=2)
    assert member.display_name == "Test Nickname"

    await member.edit_nickname(None)
    with suppress(asyncio.exceptions.TimeoutError):
        await bot.wait_for("member_update", timeout=2)
    assert member.display_name == (bot.get_user(member.id)).username

    base_line = len(member.roles)

    assert len(member.roles) == base_line
    role = await guild.create_role(f"test-{bot.suffix}")
    try:
        await member.add_role(role)
        with suppress(asyncio.exceptions.TimeoutError):
            await bot.wait_for("member_update", timeout=2)
        assert len(member.roles) != base_line
        await member.remove_role(role)
        with suppress(asyncio.exceptions.TimeoutError):
            await bot.wait_for("member_update", timeout=2)
        assert len(member.roles) == base_line

        assert member.display_avatar is not None
        assert member.display_name is not None

        assert member.has_permission(Permissions.SEND_MESSAGES)
        assert member.channel_permissions(channel)

        assert member.guild_permissions is not None
    finally:
        await role.delete()


@pytest.mark.asyncio
async def test_gateway(bot: Client) -> None:
    try:
        gateway: WebsocketClient = bot._connection_state.gateway

        assert gateway._entered
        assert gateway._keep_alive is not None

        await bot.change_presence(Status.DO_NOT_DISTURB, activity="Testing")
        await bot.change_presence()

        await gateway.send_heartbeat()
        await gateway._acknowledged.wait()
    finally:
        await bot.change_presence(activity="Testing someones code")


@pytest.mark.asyncio
async def test_ratelimit(bot: Client, channel: GuildText) -> None:
    msg = await channel.send("- Abusing the api... please wait")
    await msg.add_reaction("🤔")
    await msg.remove_reaction("🤔")

    limit = bot.http.get_ratelimit(
        Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
            channel_id=msg.channel.id,
            message_id=msg.id,
            emoji=process_emoji_req_format("🤔"),
        )
    )
    await msg.add_reaction("🤔")
    await msg.remove_reaction("🤔")
    assert limit.locked
    await msg.add_reaction("🤔")
    await msg.remove_reaction("🤔")
    assert limit.locked


@pytest.mark.asyncio
async def test_embeds(bot: Client, channel: GuildText) -> None:
    msg = await channel.send("Embed Tests")
    thread = await msg.create_thread("Test Thread")

    try:
        e = Embed("Test")
        await thread.send(embeds=e)

        e = Embed(
            "Test",
            "Test",
            BrandColors.RED,
            "https://github.com/",
            datetime.now(),
            [
                EmbedField("name", "value"),
                EmbedField("name2", "value2"),
                EmbedField("name3", "value3"),
            ],
            EmbedAuthor(bot.user.display_name, bot.user.avatar.url),
            EmbedAttachment(bot.user.avatar.url),
            EmbedAttachment(bot.owner.avatar.url),
            footer=EmbedFooter("Test", icon_url=bot.user.avatar.url),
        )
        await thread.send(embeds=e)

        e = Embed("Test")
        e.color = BrandColors.RED
        e.url = "https://github.com/"
        e.timestamp = datetime.now()
        e.set_image(bot.user.avatar.url)
        e.set_thumbnail(bot.user.avatar.url)
        e.set_author("Test", bot.owner.avatar.url)
        e.set_footer("Test")
        e.add_field("test", "test")
        e.add_field("test2", "test2")
        await thread.send(embeds=e)

        await thread.delete()
    finally:
        with suppress(interactions.errors.NotFound):
            await thread.delete()


@pytest.mark.asyncio
async def test_components(bot: Client, channel: GuildText) -> None:
    msg = await channel.send("Component Tests")
    thread = await msg.create_thread("Test Thread")

    try:
        await thread.send("Test - single", components=Button(style=ButtonStyle.PRIMARY, label="test"))
        await thread.send(
            "Test - list",
            components=[
                Button(style=ButtonStyle.PRIMARY, label="test"),
                Button(style=ButtonStyle.PRIMARY, label="test"),
            ],
        )
        await thread.send(
            "Test - ActionRow",
            components=ActionRow(
                *[Button(style=ButtonStyle.PRIMARY, label="test"), Button(style=ButtonStyle.PRIMARY, label="test")]
            ),
        )
        await thread.send(
            "Test - StringSelectMenu",
            components=StringSelectMenu(StringSelectOption(label="test", value="test")),
        )

        Modal(ParagraphText(label="test", value="test value, press send"), title="Test Modal")

    finally:
        with suppress(interactions.errors.NotFound):
            await thread.delete()


@pytest.mark.asyncio
async def test_webhooks(bot: Client, guild: Guild, channel: GuildText) -> None:
    test_thread = await channel.create_thread("Test Thread")

    hook = await channel.create_webhook("Test")
    await hook.send("Test 123")
    await hook.delete()

    hook = await channel.create_webhook("Test-Avatar", r"tests/LordOfPolls.png")

    _m = await hook.send("Test", wait=True)
    assert isinstance(_m, Message)
    assert _m.webhook_id == hook.id
    await hook.send("Test", username="Different Name", wait=True)
    await hook.send("Test", avatar_url=bot.user.avatar.url, wait=True)
    _m = await hook.send("Test", thread=test_thread, wait=True)
    assert _m is not None
    assert _m.channel == test_thread

    await hook.delete()


@pytest.mark.asyncio
async def test_voice(bot: Client, guild: Guild) -> None:
    test_channel = await guild.create_voice_channel(f"_test_voice-{bot.suffix}")
    test_channel_two = await guild.create_voice_channel(f"_test_voice_two-{bot.suffix}")
    try:
        try:
            import nacl  # noqa
        except ImportError:
            # testing on a non-voice extra
            return

        vc = await test_channel.connect(deafened=True)
        assert vc == bot.get_bot_voice_state(guild.id)

        audio = AudioVolume("tests/test_audio.mp3")
        vc.play_no_wait(audio)
        await asyncio.sleep(5)

        assert len(vc.current_audio.buffer) != 0
        assert vc.player._sent_payloads != 0

        await vc.move(test_channel_two)
        await asyncio.sleep(2)

        _before = vc.player._sent_payloads

        await test_channel_two.connect(deafened=True)

        await asyncio.sleep(2)

        assert vc.player._sent_payloads != _before

        vc.volume = 1
        await asyncio.sleep(1)
        vc.volume = 0.5

        vc.pause()
        await asyncio.sleep(0.1)
        assert vc.player.paused
        vc.resume()
        await asyncio.sleep(0.1)
        assert not vc.player.paused

        await vc.disconnect()
        await vc._close_connection()
        await vc.ws._closed.wait()
    finally:
        await test_channel.delete()
        await test_channel_two.delete()


@pytest.mark.asyncio
async def test_emoji(bot: Client, guild: Guild) -> None:
    emoji = None
    try:
        emoji = await guild.create_custom_emoji("testEmoji", r"tests/LordOfPolls.png")
        assert emoji.animated is False

        fetched_emoji = await bot.fetch_custom_emoji(emoji.id, guild.id)

        assert emoji == fetched_emoji
        assert emoji.animated == fetched_emoji.animated
        ensure_attributes(emoji)
        ensure_attributes(fetched_emoji)

        await emoji.edit(name="testEditedName")
        await asyncio.sleep(1)
        fetched_emoji = await bot.fetch_custom_emoji(emoji.id, guild.id)
        assert fetched_emoji.name == "testEditedName"

    finally:
        if emoji:
            await emoji.delete()
