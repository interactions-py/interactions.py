"""
A bunch of fake API responses for testing.

Because the library has a habit of mangling the data (_process_dict), these are functions that will always return clean responses.
"""

import random
import typing
import discord_typings
from typing import Optional

__all__ = ("SAMPLE_DM_DATA", "SAMPLE_GUILD_DATA", "SAMPLE_USER_DATA")


def SAMPLE_USER_DATA(user_id: Optional[str] = None) -> discord_typings.UserData:
    if user_id is None:
        user_id = "123456789012345678"

    return {
        "id": user_id,
        "username": "test_user",
        "discriminator": "1234",
        "avatar": "",
    }


def SAMPLE_DM_DATA() -> discord_typings.DMChannelData:
    return {
        "id": "123456789012345679",
        "type": 1,
        "last_message_id": None,
        "recipients": [SAMPLE_USER_DATA()],
    }


def SAMPLE_CHANNEL_DATA(
    channel_id: Optional[str] = None, guild_id: Optional[str] = None
) -> discord_typings.ChannelData:
    if channel_id is None:
        channel_id = "123456789012345678"
    return {
        "id": channel_id,
        "type": 0,
        "guild_id": guild_id,
        "name": "test_channel",
        "topic": "",
        "position": 0,
        "permission_overwrites": [],
        "bitrate": 0,
        "user_limit": 0,
        "rate_limit_per_user": 0,
        "last_message_id": None,
        "permissions": 0,
        "nsfw": False,
    }


def SAMPLE_GUILD_DATA(guild_id: Optional[str] = None) -> discord_typings.GuildData:
    if guild_id is None:
        guild_id = "123456789012345670"
    return {
        "id": guild_id,
        "name": "test_guild",
        "icon": "",
        "splash": "",
        "discovery_splash": "",
        "owner_id": "123456789012345678",
        "afk_channel_id": None,
        "afk_timeout": 0,
        "verification_level": 0,
        "default_message_notifications": 0,
        "explicit_content_filter": 0,
        "roles": [],
        "emojis": [],
        "features": [],
        "mfa_level": 0,
        "application_id": None,
        "system_channel_id": None,
        "system_channel_flags": 0,
        "rules_channel_id": None,
        "vanity_url_code": None,
        "description": None,
        "banner": None,
        "premium_tier": 0,
        "preferred_locale": "en-US",
        "public_updates_channel_id": None,
        "nsfw_level": 0,
        "stickers": [],
        "premium_progress_bar_enabled": False,
    }


def SAMPLE_MESSAGE_DATA(
    channel_id: Optional[str] = None,
    user_id: Optional[str] = None,
    message_id: Optional[str] = None,
    guild_id: Optional[str] = None,
) -> discord_typings.MessageCreateData:
    if channel_id is None:
        channel_id = "123456789012345678"
    if message_id is None:
        message_id = "123456789012345677"
    data = {
        "id": message_id,
        "channel_id": channel_id,
        "author": SAMPLE_USER_DATA(user_id),
        "content": "test_message",
        "timestamp": "2022-07-16T20:56:55.999419+01:00",
        "edited_timestamp": None,
        "tts": False,
        "mention_everyone": False,
        "mentions": [SAMPLE_USER_DATA(user_id)],
        "mention_roles": [],
        "mention_channels": [],
        "attachments": [],
        "embeds": [],
        "reactions": [],
        "nonce": None,
        "pinned": False,
        "webhook_id": None,
        "type": 0,
        "activity": None,
        "application": None,
        "application_id": None,
        "message_reference": None,
        "flags": 0,
        "refereces_message": None,
        # "interaction": None,
        "thread": None,
        "components": [],
        "sticker_items": [],
    }
    if guild_id is not None:
        data["guild_id"] = guild_id
    return data


def SAMPLE_LOCALE() -> str:
    options = typing.get_args(discord_typings.Locales)
    return random.sample(options, 1)[0]  # type: ignore


def SAMPLE_APPLICATION_DATA(owner: typing.Optional[discord_typings.UserData]) -> discord_typings.ApplicationData:
    return {
        "id": "10001000010001",
        "name": "Sample Application",
        "description": "Mock data, this is not a real bot.",
        "rpc_origins": [],
        "bot_public": False,
        "bot_require_code_grant": False,
        "owner": owner,
        "verify_key": "",
        "summary": "",
        "icon": None,
        "team": None,
    }
