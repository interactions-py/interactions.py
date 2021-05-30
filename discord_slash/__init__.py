"""
discord-py-slash-command
~~~~~~~~~~~~~~~~~~~~~~~~

Simple Discord Slash Command extension for discord.py

:copyright: (c) 2020-2021 eunwoo1104
:license: MIT
"""

from .client import SlashCommand
from .model import SlashCommandOptionType
from .context import SlashContext
from .utils import manage_commands
from .utils import manage_components

__version__ = "1.2.0"
