# Normal libraries
from asyncio import create_task, sleep
from contextlib import suppress
from enum import IntEnum
import typing
from typing import (
    Any,
    Coroutine,
    List,
    Optional,
    Union
)

# 3rd-party libraries
from discord import (
    DMChannel,
    GroupChannel,
    TextChannel,
    Member
)
from discord.abc import GuildChannel, Messageable, Role, User
from discord.errors import Forbidden
from discord.state import ConnectionState
from .error import IncorrectCommandData, IncorrectFormat
from .http import MessageRequest
from .override import BaseMessage

class Command:
    """
    Object representing application commands.

    .. warning::

        Do not manually initialize this class.

    :ivar _type:
    :ivar name:
    :ivar description:
    :ivar allowed_guild_ids:
    :ivar options:
    :ivar connector:
    """
    __slots__ = (
        "_type",
        "name",
        "description",
        "allowed_guild_ids",
        "options",
        "connector"
    )
    _type: IntEnum
    name: str
    description: str
    guild_ids: Optional[List[int]]
    options: Optional[List[dict]]
    connector: Optional[dict]
    permissions: Optional[List[dict]]
    default_permission: Optional[bool]
    has_options: bool
    has_subcommands: bool
    has_permissions: bool

    def __init__(
        self,
        name,
        command: dict,
        _type: Optional[IntEnum]=1
    ) -> None:
        """
        Instantiates the Command class.

        :param name: The name of the slash command.
        :type name: str
        :param command: A dictionary set of keys with values assigned 
        :type command: dict
        :param _type: The type of application command.
        :type _type: enum.IntEnum
        :return: None
        """
        super().__init__(command["func"])
        self._type = _type
        self.name = name.lower()
        self.description = command["description"]
        self.guild_ids = command["guild_ids"] or []
        self.options = command["api_options"] or []
        self.connector = command["connector"] or {}
        self.permissions = command["api_permissions"] or {}
        self.default_permission = command["default_permission"]
        self.has_options = True if self.options else False
        self.has_subcommands = True if command["has_subcommands"] else False
        self.has_permissions = True if self.permissions else False
        
class Subcommand(Command):
    """
    Object for representing slash subcommands.

    .. note::
        
        This extends off of :class:`.model.Command`.

    .. warning::

        Do not manually initialize this class.

    :ivar base:
    :ivar group:
    :ivar base_description:
    :ivar group_description:
    :inherit: Command
    """
    __slots__ = (
        "base",
        "group",
        "base_description",
        "group_description",
        "has_group"
    )
    base: str
    group: str
    base_description: str
    group_description: str
    has_group: bool

    def __init__(
        self,
        command: Any,
        base: str,
        name: str,
        group: Optional[str]=None
    ) -> None:
        """
        Instantiates the Subcommand class.

        :param command: The inherited command values.
        :type command: typing.Any
        :param base: The name of the "base" (overall) command.
        :type base: str
        :param name: The name of the subcommand.
        :type name: str
        :param group: A subset category "grouping" of the base. Defaults to `None`.
        :type group: typing.Optional[str]
        :return: None
        """
        # command is not Any but dict, but I cba. ¯\_(ツ)_/¯
        super().__init__(
            command,
            base
        )
        self.base = base.lower()
        self.group = group.lower() if group else group
        self.base_description = command["base_desc"]
        self.group_description = command["sub_group_desc"]
        self.has_group = True if self.group else False

class CogCommand(Command):
    """
    Object for representing commands registered under a cog.

    .. note::

        This extends off of :class:`.model.Command`. 
    
    .. warning::

        Do not manually initialize this class.

    :ivar cog:
    """
    __slots__ = "cog"
    cog: Any
    
    def __init__(
        self,
        *args
    ) -> None:
        """
        Instantiates the CogCommand class.
        
        :param \*args: Multi-argument for command information.
        :return: None
        """
        super().__init__(*args)
        self.cog = None

class BaseCommand:
    """
    Object that represents data for a slash command.
    
    :ivar name:
    :ivar description:
    :ivar default_permission:
    :ivar options:
    :ivar id:
    :ivar application_id:
    """
    __slots__ = (
        "name",
        "description",
        "options",
        "default_permission",
        "id",
        "application_id",
        "version"
    )
    name: str
    description: str
    options: Optional[list]
    default_permission: Optional[bool]
    id: Optional[int]
    application_id: Optional[int]
    version: str

    def __init__(
        self,
        name: str,
        description: str,
        options: Optional[list]=[],
        default_permission: Optional[bool]=True,
        id: Optional[int]=None,
        application_id: Optional[int]=None,
        version: Optional[str]=None,
        **kwargs
    ) -> None:
        """
        Instantiates the Command class.
        
        :param name: The name of the slash command.
        :type name: str
        :param description: The description of the slash command.
        :type description: str
        :param options: The arguments/so-called "options" of the slash command.
        :type options: typing.Optional[list]
        :param default_permission: Whether the user should have access to the slash command by default or not.
        :type default_permission: typing.Optional[bool]
        :param id: The unique ID/identifier of the slash command.
        :type id: typing.Optional[int]
        :param application_id: The application ID of the bot.
        :type application_id: typing.Optional[int]
        :param version: The current version of the application command. Defaults to `None`.
        :type version: typing.Optional[str]
        :param \**kwargs: Keyword-arguments to pass.
        :return: None
        """
        self.name = name
        self.description = description
        self.default_permission = default_permission
        self.id = id
        self.application_id = application_id
        self.version = version
        self.options = []
        if options is not []:
            [self.options.append(BaseOption(**option)) for option in options]

    def __eq__(
        self,
        other
    ):
        if isinstance(other, BaseCommand):
            return (
                self.name == other.name
                and self.description == other.description
                and self.options == other.options
                and self.default_permission == other.default_permission
            )
        else:
            return False

class BaseOption:
    """
    Object that represents data for a slash command's option.

    :ivar name:
    :ivar description:
    :ivar required:
    :ivar options:
    :ivar choices:
    """
    __slots__ = (
        "name",
        "description",
        "required",
        "options",
        "choices"
    )
    name: str
    description: str
    required: Optional[bool]
    options: Optional[list]
    choices: Optional[list]

    def __init__(
        self,
        name: str,
        description: str,
        required: Optional[bool]=False,
        options: Optional[list]=[],
        choices: Optional[list]=[],
        **kwargs
    ) -> None:
        """
        Instantiates the OptionData class.

        :param name: The name of the option.
        :type name: str
        :param description: The description of the option.
        :type description: str
        :param required: Whether the option has to be filled when running the slash command or not.
        :type required: typing.Optional[bool]
        :param options: A list of options recursively from ``OptionData``. This only shows if a subcommand is present.
        :type options: typing.Optional[list]
        :param choices: A list of pre-defined values/"choices" for the option.
        :type choices: typing.Optional[list]
        :param \**kwargs: Keyword-arguments to pass.
        :raises: .error.IncorrectCommandData
        :return None:
        """
        self.name = name
        self.description = description
        self.required = required
        self.options, self.choices = []
        _type = kwargs.get("type")
        if _type == None:
            raise IncorrectCommandData("type is a required kwarg for options.")
        if _type in [1, 2]:
            if options is not []:
                [self.options.append(BaseOption(**option)) for option in options]
            elif _type == 2:
                raise IncorrectCommandData("Options are required for subcommands/subcommand groups.")
        if choices != []:
            [self.choices.append(BaseChoice(**choice)) for choice in choices]

    def __eq__(
        self,
        other
    ):
        return isinstance(other, BaseOption) and self.__dict__ == other.__dict__

class BaseChoice:
    """
    Object representing data for a slash command option's choice(s).
    
    :ivar name:
    :ivar value:
    """
    __slots__ = "name", "value"
    name: str
    value: Union[str, int, bool]

    def __init__(
        self,
        name: str,
        value: Union[str, int, bool]
    ) -> None:
        """
        Instantiates the Choice class.
        
        :param name: The name of the choice.
        :type name: str
        :param value: The returned content/value of the choice.
        :type value: typing.Union[str, int, bool]
        :return: None
        """
        self.name = name
        self.value = value

    def __eq__(
        self,
        other
    ):
        return isinstance(other, BaseChoice) and self.__dict__ == other.__dict__

class BasePermission:
    """
    Object representing the data for a slash command's permission(s).

    :ivar id:
    :ivar _type:
    :ivar state:
    """
    __slots__ = "id", "_type", "state"
    id: int
    _type: IntEnum
    state: bool

    def __init__(
        self,
        id: str,
        _type: IntEnum,
        state: bool,
        **kwargs
    ) -> None:
        """
        Instantiates the Permission class.

        :param id: A role/user ID given for the permission to check for.
        :type id: int
        :param _type: The permission data type respectively to ``id``.
        :type _type: enum.IntEnum
        :param state: The state of the permission to whether allow or disallow access. Passed as `True`/`False` respectively.
        :type state: bool
        :param \**kwargs: Keyword-arguments to pass.
        :return: None
        """
        self.id = id
        self._type = _type
        self.state = state

    def __eq__(
        self,
        other
    ):
        if isinstance(other, BasePermission):
            return (
                self.id == other.id
                and self._type == other.id
                and self.state == other.state
            )
        else:
            return False

class BaseGuildPermission:
    """
    Object for representing data for permission(s) relating to a guild slash command.

    :ivar id:
    :ivar guild_id:
    :ivar permissions:
    """
    __slots__ = "id", "guild_id", "permissions"
    id: int
    guild_id: int
    permissions: List[dict]

    def __init__(
        self,
        id: int,
        guild_id: int,
        permissions: List[dict]
    ) -> None:
        """
        Instantiates the GuildPermission class.

        :param id: The unique ID/identifier of the slash command.
        :type id: int
        :param guild_id: The ID of the guild the guild slash command is registered under.
        :type guild_id: int
        :param permissions: A list of permissions for the guild slash command.
        :type permissions: typing.List[dict]
        :return: None
        """
        self.id = id
        self.guild_id = guild_id
        self.permissions = []
        if permissions != {}:
            [self.permissions.append(BaseGuildPermission(**permission)) for permission in permissions]

    def __eq__(
        self,
        other
    ):
        if isinstance(other, BaseGuildPermission):
            return (
                self.id == other.id
                and self.guild_id == other.guild_id
                and self.permissions == other.permissions
            )
        else:
            return False

class Message(BaseMessage):
    """
    Object for representing data of a slash command message.

    .. note::

        This extends off of `discord.Message <https://github.com/Rapptz/discord.py/blob/master/discord/message.py#L487>`_ from discord.py.
        The ``edit`` and ``delete`` methods have been overwritten in order to allow slash commands to function seamlessly.
    """
    _http: MessageRequest
    __interaction_token: int

    def __init__(
        self,
        *,
        state: ConnectionState,
        channel: Union[TextChannel, DMChannel, GroupChannel],
        data: Any,
        _http: MessageRequest,
        interaction_token: int
    ) -> None:
        """
        Instantiates the Message class.

        :param state: The current asynchronous state of connection.
        :type state: discord.state.ConnectionState
        :param channel: The channel the message came from.
        :type channel: typing.Union[discord.TextChannel, discord.DMChannel, discord.GroupChannel]
        :param data: The data to pass through the message.
        :type data: typing.Any
        :param _http: The HTTP interaction request handler.
        :type _http: .http.InteractionHTTP
        :param interaction_token: The token of the interaction event.
        :type interaction_token: int
        :raises: .error.IncorrectFormat
        :return: None
        """
        super().__init__(
            state=state,
            channel=channel,
            data=data
        )
        self._http = _http
        self.__interaction_token = interaction_token
        
    async def _slash_edit(
        self,
        **fields
    ) -> Coroutine:
        _response: dict = {}
        try:
            content = fields["content"]
            components = fields["components"]
            embed = fields["embed"]
            embeds = fields["embeds"]
            file = fields["file"]
            files = fields["files"]
            allowed_mentions = fields.get("allowed_mentions")
            delete_after = fields.get("delete_after")
        except KeyError:
            pass
        else:
            content = str(content) if content is None else None
            _response["components"] = [] if components is None else components
            _response["embeds"] = [embed.to_dict() for embed in embeds]
            _response["embeds"] = [] if embed == None else ([embed.to_dict()] if embeds is None else _response["embeds"])
            files = [file] if file else files
            if not isinstance(embeds, list):
                raise IncorrectFormat("Provide a list of embeds.")
            if len(embeds) > 10:
                raise IncorrectFormat("Do not provide more than 10 embeds.")
            if (
                files is not None and
                file is not None
            ):
                raise IncorrectFormat("You can't use both file and files kwargs at the same time.")
            if allowed_mentions is None:
                if self._state.allowed_mentions is None:
                    _response["allowed_mentions"] = self._state.allowed_mentions.merge(
                        allowed_mentions
                    ).to_dict()
                else:
                    _response["allowed_mentions"] = allowed_mentions.to_dict()
            else:
                if self._state.allowed_mentions is None:
                    _response["allowed_mentions"] = self._state.allowed_mentions.to_dict()
                else:
                    _response["allowed_mentions"] = {}
            if delete_after:
                await self.delete(delay=delete_after)
            [[file.close() for file in files] if files else None]
            
    async def delete(
        self,
        *,
        delay: Optional[int]=None
    ) -> Coroutine:
        """
        Please refer to :meth:`discord.Message.delete` for documentation.
        """
        try:
            await super().delete(delay=delay)
        except Forbidden:
            if not delay:
                return await self._http.delete(
                    self.__interaction_token,
                    self.id
                )
            async def wrap():
                with suppress(Forbidden):
                    await sleep(delay)
                    await self._http.delete(
                        self.__interaction_token,
                        self.id
                    )
            self._state.loop.create_task(wrap())

class BaseMenu:
    """
    Object for representing data for command(s) of a contextual menu.

    :ivar _type:
    :ivar name:
    """
    __slots__ = "_type", "name"
    _type: IntEnum
    name: str

    def __init__(
        self,
        name: str,
        _type: IntEnum
    ) -> None:
        """
        Instantiates the BaseMenu class.

        :param name: The name of the application command.
        :type name: str
        :param _type: The type of application command.
        :type _type: enum.IntEnum
        :return: None
        """

    def __eq__(
        self,
        other
    ):
        if isinstance(other, BaseMenu):
            return (
                self.id == other.id
                and self._type == other.id
                and self.state == other.state
            )
        else:
            return False
    
class Options(IntEnum):
    """
    Enumerable object of literal integers holding equivocal values of a slash command's option(s).

    .. note::

        Equivalent of `ApplicationCommandOptionType <https://discord.com/developers/docs/interactions/slash-commands#applicationcommandoptiontype>`_ in the Discord API.
    """
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
    MENTIONABLE = 9
    FLOAT = 10

    @classmethod
    def from_type(
        cls,
        _type: type
    ) -> IntEnum:
        """
        Get a specific enumerable from a type or object.

        :param _type: The type or object to get an enumerable integer for.
        :type _type: type
        :return: enum.IntEnum.
        """
        if issubclass(_type, str):
            return cls.STRING
        if issubclass(_type, int):
            return cls.INTEGER
        if issubclass(_type, bool):
            return cls.BOOLEAN
        if issubclass(_type, User):
            return cls.USER
        if issubclass(_type, GuildChannel):
            return cls.CHANNEL
        if issubclass(_type, Role):
            return cls.ROLE
        if (
            hasattr(typing, "_GenericAlias")
            and isinstance(_type, typing._UnionGenericAlias) # noqa
            or not hasattr(typing, "_GenericAlias")
            and isinstance(_type, typing._Union) # noqa
        ):
            return cls.MENTIONABLE
        if issubclass(_type, float):
            return cls.FLOAT

class Permissions(IntEnum):
    """
    Enumerable object of literal integers holding equivocal values of a slash command's permission(s).

    .. note::

        Equivalent of `ApplicationCommandPermissionType <https://discord.com/developers/docs/interactions/slash-commands#applicationcommandpermissiontype>`_ in the Discord API.
    """
    ROLE = 1
    USER = 2

    @classmethod
    def from_type(
        cls,
        _type: type
    ) -> IntEnum:
        """
        Get a specific enumerable from a type or object.

        :param _type: The type or object to get an enumerable integer for.
        :type _type: type
        :return: enum.IntEnum.
        """
        if issubclass(_type, Role):
            return cls.ROLE
        if issubclass(_type, User):
            return cls.USER

class Components(IntEnum):
    """
    Enumerable object of literal integers holding equivocal values of a component(s) type.
    
    .. note::

        Equivalent of `Component Types <https://discord.com/developers/docs/interactions/message-components#component-object-component-types>`_ in the Discord API.
    """
    ACTION_ROW = 1
    BUTTON = 2
    SELECT = 3

class Buttons(IntEnum):
    """
    Enumerable object of literal integers holding equivocal values of a button(s) type.
    
    .. note::

        Equivalent of `Button Styles <https://discord.com/developers/docs/interactions/message-components#button-object-button-styles>`_ in the Discord API.
    """
    BLUE = 1
    BLURPLE = 2
    GRAY = 2
    GREY = 2
    GREEN = 3
    RED = 4

    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    URL = 5

class Menus(IntEnum):
    """
    Enumerable object of literal integers holding equivocal values of a menu type for commands.

    .. note::

        Equivalent of `Application Command Types <https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-types>`_ in the Discord API.
    """
    CHAT_INPUT = 1
    COMMAND = 1 # alias of CHAT_INPUT
    USER = 2
    MESSAGE = 3

    @classmethod
    def from_type(
        cls,
        _type: type
    ) -> type:
        """
        Get a specific enumerable from a type or object.

        :param _type: The type or object to get an enumerable integer for.
        :type _type: type
        :return: enum.IntEnum.
        """
        if (
            isinstance(_type, Member) or
            issubclass(_type, User)
        ):
            return cls.USER
        if issubclass(_type, Messageable):
            return cls.MESSAGE