import discord
import asyncio

from discord.ext import commands
from discord.ext.commands.core import (
    GroupMixin,
    CommandRegistrationError,
    _convert_to_bool
)
from typing import (
    get_origin,
    get_args,
    Union
)

from .application import OptionType

TYPE_MAP = [
    (lambda val: val is str, OptionType.string, commands.UserConverter),
    (lambda val: val is int, OptionType.integer, int),
    (lambda val: val is bool, OptionType.boolean, None), 
    (lambda val: val is discord.User, OptionType.user, commands.UserConverter),
    (lambda val: val is discord.TextChannel, OptionType.channel, commands.TextChannelConverter),
    (lambda val: val is discord.Role, OptionType.role, commands.RoleConverter)
]

class GroupMixin(commands.GroupMixin):
    def __init__(self, *args, **kwargs):
        self.application_commands = {}
        self.message_commands = {}
        self.mixed_commands = {}
        super().__init__(*args, **kwargs)
        self.application_commands = self._dict_type()
        self.message_commands = self._dict_type()
        self.mixed_commands = self._dict_type()

    @property
    def commands(self):
        return set(self.application_commands.values()) | set(self.message_commands.values()) | set(self.mixed_commands.values())

    @property
    def all_commands(self):
        return dict(list(self.application_commands.items()) + list(self.message_commands.items()) + list(self.mixed_commands.items())) #dict.__or__ isn't available until Python 3.9

    @all_commands.setter
    def all_commands(self, val):
        self._dict_type = type(val)

    def add_command(self, command):
        try:
            super().add_command(command) #sets attributes and does checks but only adds the command to the dict returned by all_commands
        except CommandRegistrationError: 
            pass

        if isinstance(command, Command):
            if command.interaction_allowed and command.message_allowed:
                commands = self.mixed_commands
            elif comand.interaction_allowed and not command.message_allowed:
                commands = self.application_commands
            elif command.message_allowed and not command.interaction_allowed:
                commands = self.message_commands
        else:
            commands = self.message_commands

        if command.name in commands:
            raise CommandRegistrationError(command.name)
        commands[command.name] = command

        for alias in command.aliases:
            if alias in commands:
                raise CommandRegistrationError(alias, alias_conflict=True)
            commands[alias] = command

    def remove_command(self, name):
        command = self.all_commands.pop(name, None)

        if command is None:
            return None

        if command.interaction_allowed and commands.message_allowed:
            commands = self.mixed_commands
        elif comand.interaction_allowed and not command.message_allowed:
            commands = self.application_commands
        elif command.message_allowed and not command.interaction_allowed:
            commands = self.message_commands

        commands.pop(name)

        if name in command.aliases:
            return command

        for alias in command.aliases:
            commands.pop(alias)

        return command  

    def command(self, *args, **kwargs):
        return super().command(*args, **kwargs, cls=Command)

class Command(commands.Command):
    def __init__(self, *args, **kwargs):
        self.id = None
        self.application_id = None
        self.application_guild_id = kwargs.pop('guild_id', None)
        self.interaction_allowed = kwargs.pop('interaction_allowed', False)
        self.message_allowed = kwargs.pop('message_allowed', True)
        super().__init__(*args, **kwargs)
        if self.interaction_allowed:
            self._parse_application_command()

    def _parse_application_command(self):
        options = []
        self._as_application_command = {
            'name': self.name,
            'description': self.short_doc or None,
            'options': options
        }
        for name, param in self.clean_params.items():
            if param.kind not in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD):
                raise TypeError('interaction_allowed commands can\'t handle special parsing')
            if param.default != param.empty:
                raise TypeError('interaction_allowed commands can\'t handle default values')
            if isinstance(param.annotation, InteractionCommandParameter):
                option_fields = param.annotation.to_dict()
            else:
                raise TypeError('interaction_allowed command parameter annotations should be an instance of InteractionCommandParameter')
            option_fields['name'] = name
            options.append(option_fields)

    async def _parse_arguments(self, ctx):
        if ctx.interaction is None:
            return await super()._parse_arguments(ctx)

        ctx.args = [ctx] if self.cog is None else [self.cog, ctx]
        ctx.kwargs = {}
        args = ctx.args
        kwargs = ctx.kwargs

        interaction = ctx.interaction

        iterator = iter(self.params.items())

        if self.cog is not None:
            try:
                next(iterator)
            except StopIteration:
                fmt = 'Callback for {0.name} command is missing "self" parameter.'
                raise discord.ClientException(fmt.format(self))

        try:
            next(iterator)
        except StopIteration:
            fmt = 'Callback for {0.name} command is missing "ctx" parameter.'
            raise discord.ClientException(fmt.format(self))

        for name, param in iterator:
            try:
                original_val = next(option.value for option in interaction.data.options if option.name == name)
            except StopIteration:
                original_val = None
            converter = param.annotation.converter
            try:
                try:
                    is_discord_converter = issubclass(converter, commands.Converter)
                except TypeError:
                    is_discord_converter = False
                if is_discord_converter:
                    val = await converter().convert(ctx, original_val)
                elif callable(converter):
                    val = converter(original_val)
                    if asyncio.iscoroutine(val):
                        val = await val
            except:
                val = original_val
            args.append(val)

class GetItemMeta(type):
    def __getitem__(cls, args):
        return cls(*args)

class InteractionCommandParameter( commands.Converter, metaclass=GetItemMeta):
    def __init__(self, *, description=None, option_type=None, required=True, choices=None, converter=None):
        self.description = description
        self.type_num = None
        self.converter = converter
        if option_type is not None:
            for func, type_number, converter in TYPE_MAP:
                try:
                    if func(option_type):
                        self.type_num = type_number
                        if self.converter is None:
                            self.converter = converter
                except TypeError:
                    continue
            if self.type_num is None:
                raise TypeError('{} is not an acceptable interaction_allowed command option type'.format(option_type))
        self.required = required
        self.choices = choices

    def to_dict(self):
        return {
            'description': self.description,
            'type': self.type_num,
            'required': self.required,
            'choices': self.choices
        }

    def convert(self, ctx, arg):
        return self.converter().convert(ctx, arg)