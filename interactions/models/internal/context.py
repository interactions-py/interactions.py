import abc
import datetime
import re
import typing
from typing_extensions import Self

import discord_typings
from aiohttp import FormData

from interactions.client import const
from interactions.client.const import get_logger, MISSING
from interactions.models.discord.components import BaseComponent
from interactions.models.discord.file import UPLOADABLE_TYPE
from interactions.models.discord.sticker import Sticker
from interactions.models.discord.user import Member, User

from interactions.models.internal.command import BaseCommand
from interactions.client.mixins.modal import ModalMixin

from interactions.client.errors import HTTPException, AlreadyDeferred, AlreadyResponded
from interactions.client.mixins.send import SendMixin
from interactions.models.discord.enums import (
    Permissions,
    MessageFlags,
    InteractionType,
    ComponentType,
    CommandType,
)
from interactions.models.discord.message import (
    AllowedMentions,
    Attachment,
    Message,
    MessageReference,
    process_message_payload,
)
from interactions.models.discord.snowflake import Snowflake, Snowflake_Type, to_snowflake, to_optional_snowflake
from interactions.models.discord.embed import Embed
from interactions.models.internal.application_commands import (
    OptionType,
    CallbackType,
    SlashCommandChoice,
    SlashCommandOption,
    InteractionCommand,
)

__all__ = (
    "AutocompleteContext",
    "BaseContext",
    "BaseInteractionContext",
    "ComponentContext",
    "ContextMenuContext",
    "InteractionContext",
    "ModalContext",
    "Resolved",
    "SlashContext",
)


if typing.TYPE_CHECKING:
    import interactions


class Resolved:
    """
    A class representing the resolved data from an interaction.

    Attributes:
        channels: A dictionary of channels resolved from the interaction.
        members: A dictionary of members resolved from the interaction.
        users: A dictionary of users resolved from the interaction.
        roles: A dictionary of roles resolved from the interaction.
        messages: A dictionary of messages resolved from the interaction.
        attachments: A dictionary of attachments resolved from the interaction.
    """

    def __init__(self) -> None:
        self.channels: dict[Snowflake, "interactions.TYPE_MESSAGEABLE_CHANNEL"] = {}
        self.members: dict[Snowflake, "interactions.Member"] = {}
        self.users: dict[Snowflake, "interactions.User"] = {}
        self.roles: dict[Snowflake, "interactions.Role"] = {}
        self.messages: dict[Snowflake, "interactions.Message"] = {}
        self.attachments: dict[Snowflake, "interactions.Attachment"] = {}

    def __bool__(self) -> bool:
        """Returns whether any resolved data is present."""
        return (
            bool(self.channels)
            or bool(self.members)
            or bool(self.users)
            or bool(self.roles)
            or bool(self.messages)
            or bool(self.attachments)
        )

    def get(self, snowflake: Snowflake | str, default: typing.Any = None) -> typing.Any:
        snowflake = Snowflake(snowflake)
        """Returns the value of the given snowflake."""
        if channel := self.channels.get(snowflake):
            return channel
        if member := self.members.get(snowflake):
            return member
        if user := self.users.get(snowflake):
            return user
        if role := self.roles.get(snowflake):
            return role
        if message := self.messages.get(snowflake):
            return message
        if attachment := self.attachments.get(snowflake):
            return attachment
        return default

    @classmethod
    def from_dict(cls, client: "interactions.Client", data: dict, guild_id: None | Snowflake = None) -> Self:
        instance = cls()

        if channels := data.get("channels"):
            for key, _channel in channels.items():
                instance.channels[Snowflake(key)] = client.cache.place_channel_data(_channel)

        if members := data.get("members"):
            for key, _member in members.items():
                instance.members[Snowflake(key)] = client.cache.place_member_data(
                    guild_id, {**_member, "user": {**data["users"][key]}}
                )

        if users := data.get("users"):
            for key, _user in users.items():
                instance.users[Snowflake(key)] = client.cache.place_user_data(_user)

        if roles := data.get("roles"):
            for key, _role in roles.items():
                instance.roles[Snowflake(key)] = client.cache.get_role(Snowflake(key))

        if messages := data.get("messages"):
            for key, _msg in messages.items():
                instance.messages[Snowflake(key)] = client.cache.place_message_data(_msg)

        if attachments := data.get("attachments"):
            for key, _attach in attachments.items():
                instance.attachments[Snowflake(key)] = Attachment.from_dict(_attach, client)

        return instance


class BaseContext(metaclass=abc.ABCMeta):
    """
    Base context class for all contexts.

    Define your own context class by inheriting from this class. For compatibility with the library, you must define a `from_dict` classmethod that takes a dict and returns an instance of your context class.

    """

    client: "interactions.Client"
    """The client that created this context."""

    command: BaseCommand
    """The command this context invokes."""

    author_id: Snowflake
    """The id of the user that invoked this context."""
    channel_id: Snowflake
    """The id of the channel this context was invoked in."""
    message_id: Snowflake
    """The id of the message that invoked this context."""

    guild_id: typing.Optional[Snowflake]
    """The id of the guild this context was invoked in, if any."""

    def __init__(self, client: "interactions.Client") -> None:
        self.client = client
        self.author_id = MISSING
        self.channel_id = MISSING
        self.message_id = MISSING
        self.guild_id = MISSING

    @property
    def guild(self) -> typing.Optional["interactions.Guild"]:
        """The guild this context was invoked in."""
        return self.client.cache.get_guild(self.guild_id)

    @property
    def user(self) -> "interactions.User":
        """The user that invoked this context."""
        return self.client.cache.get_user(self.author_id)

    @property
    def member(self) -> typing.Optional["interactions.Member"]:
        """The member object that invoked this context."""
        return self.client.cache.get_member(self.guild_id, self.author_id)

    @property
    def author(self) -> "interactions.Member | interactions.User":
        """The member or user that invoked this context."""
        return self.member or self.user

    @property
    def channel(self) -> "interactions.TYPE_MESSAGEABLE_CHANNEL":
        """The channel this context was invoked in."""
        if self.guild_id:
            return self.client.cache.get_channel(self.channel_id)
        return self.client.cache.get_dm_channel(self.author_id)

    @property
    def message(self) -> typing.Optional["interactions.Message"]:
        """The message that invoked this context, if any."""
        return self.client.cache.get_message(self.channel_id, self.message_id)

    @property
    def voice_state(self) -> typing.Optional["interactions.VoiceState"]:
        """The current voice state of the bot in the guild this context was invoked in, if any."""
        return self.client.cache.get_bot_voice_state(self.guild_id)

    @property
    def bot(self) -> "interactions.Client":
        return self.client

    @classmethod
    @abc.abstractmethod
    def from_dict(cls, client: "interactions.Client", payload: dict) -> Self:
        """
        Create a context instance from a dict.

        Args:
            client: The client creating this context.
            payload: The dict to create the context from.

        Returns:
            The context instance.

        """
        raise NotImplementedError


class BaseInteractionContext(BaseContext):
    token: str
    """The interaction token."""
    id: Snowflake
    """The interaction ID."""

    locale: str
    """The selected locale of the invoking user (https://discord.com/developers/docs/reference#locales)"""
    guild_locale: str
    """The selected locale of the invoking user's guild (https://discord.com/developers/docs/reference#locales)"""
    resolved: Resolved
    """The resolved data for this interaction."""

    # state info
    deferred: bool
    """Whether the interaction has been deferred."""
    responded: bool
    """Whether the interaction has been responded to."""
    ephemeral: bool
    """Whether the interaction response is ephemeral."""

    _context_type: int
    """The context type of the interaction."""
    command_id: Snowflake
    """The command ID of the interaction."""
    _command_name: str
    """The command name of the interaction."""

    permission_map: dict[Snowflake, Permissions]

    args: list[typing.Any]
    """The arguments passed to the interaction."""
    kwargs: dict[str, typing.Any]
    """The keyword arguments passed to the interaction."""

    def __init__(self, client: "interactions.Client") -> None:
        super().__init__(client)
        self.deferred = False
        self.responded = False
        self.ephemeral = False

    @classmethod
    def from_dict(cls, client: "interactions.Client", payload: dict) -> Self:
        instance = cls(client=client)
        instance.token = payload["token"]
        instance.id = Snowflake(payload["id"])
        instance.permission_map = {client.app.id: Permissions(payload.get("app_permissions", 0))}
        instance.locale = payload["locale"]
        instance.guild_locale = payload.get("guild_locale", instance.locale)
        instance._context_type = payload.get("type", 0)
        instance.resolved = Resolved.from_dict(client, payload["data"].get("resolved", {}), payload.get("guild_id"))

        instance.channel_id = Snowflake(payload["channel_id"])
        if member := payload.get("member"):
            instance.author_id = Snowflake(member["user"]["id"])
            instance.guild_id = Snowflake(payload["guild_id"])
            client.cache.place_member_data(instance.guild_id, member)
        else:
            instance.author_id = Snowflake(payload["user"]["id"])
            client.cache.place_user_data(payload["user"])

        if message_data := payload.get("message"):
            message = client.cache.place_message_data(message_data)
            instance.message_id = message.id

        instance.guild_id = to_optional_snowflake(payload.get("guild_id"))

        if payload["type"] in (InteractionType.APPLICATION_COMMAND, InteractionType.AUTOCOMPLETE):
            instance.command_id = Snowflake(payload["data"]["id"])
            instance._command_name = payload["data"]["name"]

        instance.process_options(payload)

        if member := payload.get("member"):
            instance.permission_map[Snowflake(member["id"])] = Permissions(member["permissions"])

        return instance

    @property
    def app_permissions(self) -> Permissions:
        """The permissions available to this interaction"""
        return self.permission_map.get(self.client.app.id, Permissions(0))

    @property
    def author_permissions(self) -> Permissions:
        """The permissions available to the author of this interaction"""
        if self.guild_id:
            return self.permission_map.get(self.author_id, Permissions(0))
        return Permissions(0)

    @property
    def command(self) -> InteractionCommand:
        return self.client._interaction_lookup[self._command_name]

    @property
    def expires_at(self) -> typing.Optional[datetime.datetime]:
        """The time at which the interaction expires."""
        if self.responded:
            return self.id.created_at + datetime.timedelta(minutes=15)
        return self.id.created_at + datetime.timedelta(seconds=3)

    @property
    def expired(self) -> bool:
        """Whether the interaction has expired."""
        return datetime.datetime.utcnow() > self.expires_at

    @property
    def invoke_target(self) -> str:
        """The invoke target of the interaction."""
        return self._command_name

    @property
    def deferred_ephemeral(self) -> bool:
        """Whether the interaction has been deferred ephemerally."""
        return self.deferred and self.ephemeral

    def option_processing_hook(self, option: dict) -> typing.Any:
        """
        Hook for extending options processing.

        This is called for each option, before the library processes it. If this returns a value, the library will not process the option further.

        Args:
            option: The option to process.

        Returns:
            The processed option.

        """
        return option

    def process_options(self, data: discord_typings.InteractionCallbackData) -> None:
        if data["type"] not in (InteractionType.APPLICATION_COMMAND, InteractionType.AUTOCOMPLETE):
            self.args = []
            self.kwargs = {}
            return

        def gather_options(_options: list[dict[str, typing.Any]]) -> dict[str, typing.Any]:
            """Recursively gather options from an option list."""
            kwargs = {}
            for option in _options:
                if hook_result := self.option_processing_hook(option):
                    kwargs[option["name"]] = hook_result

                if option["type"] in (OptionType.SUB_COMMAND, OptionType.SUB_COMMAND_GROUP):
                    self._command_name = f"{self._command_name} {option['name']}"
                    return gather_options(option["options"])

                value = option.get("value")

                if option["type"] in OptionType.resolvable_types():
                    value = self.resolved.get(value, value)

                kwargs[option["name"]] = value
            return kwargs

        if options := data["data"].get("options"):
            self.kwargs = gather_options(options)  # type: ignore
        else:
            self.kwargs = {}
        self.args = list(self.kwargs.values())


class InteractionContext(BaseInteractionContext, SendMixin):
    async def defer(self, *, ephemeral: bool = False) -> None:
        """
        Defer the interaction.

        Args:
            ephemeral: Whether the interaction response should be ephemeral.
        """
        if self.deferred:
            raise AlreadyDeferred("Interaction has already been responded to.")
        if self.responded:
            raise AlreadyResponded("Interaction has already been responded to.")

        payload = {"type": CallbackType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE}
        if ephemeral:
            payload["data"] = {"flags": MessageFlags.EPHEMERAL}

        await self.client.http.post_initial_response(payload, self.id, self.token)
        self.deferred = True
        self.ephemeral = ephemeral

    async def _send_http_request(
        self, message_payload: dict, files: typing.Iterable["UPLOADABLE_TYPE"] | None = None
    ) -> dict:
        if const.has_client_feature("FOLLOWUP_INTERACTIONS_FOR_IMAGES") and not self.deferred and not self.responded:
            # experimental bypass for discords broken image proxy
            if embeds := message_payload.get("embeds", {}):
                if any(e.get("image") for e in embeds) or any(e.get("thumbnail") for e in embeds):
                    if MessageFlags.EPHEMERAL in message_payload.get("flags", MessageFlags.NONE):
                        self.ephemeral = True
                    await self.defer(ephemeral=self.ephemeral)

        if self.responded:
            message_data = await self.client.http.post_followup(
                message_payload, self.client.app.id, self.token, files=files
            )
        else:
            if isinstance(message_payload, FormData) and not self.deferred:
                await self.defer(ephemeral=self.ephemeral)
            if self.deferred:
                if const.has_client_feature("FOLLOWUP_INTERACTIONS_FOR_IMAGES"):
                    message_data = await self.client.http.post_followup(
                        message_payload, self.client.app.id, self.token, files=files
                    )
                else:
                    message_data = await self.client.http.edit_interaction_message(
                        message_payload, self.client.app.id, self.token, files=files
                    )
            else:
                payload = {
                    "type": CallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": message_payload,
                }
                message_data = await self.client.http.post_initial_response(payload, self.id, self.token, files=files)

        if not message_data:
            try:
                message_data = await self.client.http.get_interaction_message(self.client.app.id, self.token)
            except HTTPException:
                pass

        self.responded = True
        return message_data

    async def send(
        self,
        content: typing.Optional[str] = None,
        *,
        embeds: typing.Optional[
            typing.Union[typing.Iterable[typing.Union["Embed", dict]], typing.Union["Embed", dict]]
        ] = None,
        embed: typing.Optional[typing.Union["Embed", dict]] = None,
        components: typing.Optional[
            typing.Union[
                typing.Iterable[typing.Iterable[typing.Union["BaseComponent", dict]]],
                typing.Iterable[typing.Union["BaseComponent", dict]],
                "BaseComponent",
                dict,
            ]
        ] = None,
        stickers: typing.Optional[
            typing.Union[
                typing.Iterable[typing.Union["Sticker", "Snowflake_Type"]],
                "Sticker",
                "Snowflake_Type",
            ]
        ] = None,
        allowed_mentions: typing.Optional[typing.Union["AllowedMentions", dict]] = None,
        reply_to: typing.Optional[typing.Union["MessageReference", "Message", dict, "Snowflake_Type"]] = None,
        files: typing.Optional[typing.Union["UPLOADABLE_TYPE", typing.Iterable["UPLOADABLE_TYPE"]]] = None,
        file: typing.Optional["UPLOADABLE_TYPE"] = None,
        tts: bool = False,
        suppress_embeds: bool = False,
        silent: bool = False,
        flags: typing.Optional[typing.Union[int, "MessageFlags"]] = None,
        delete_after: typing.Optional[float] = None,
        ephemeral: bool = False,
        **kwargs: typing.Any,
    ) -> "interactions.Message":
        """
        Send a message.

        Args:
            content: Message text content.
            embeds: Embedded rich content (up to 6000 characters).
            embed: Embedded rich content (up to 6000 characters).
            components: The components to include with the message.
            stickers: IDs of up to 3 stickers in the server to send in the message.
            allowed_mentions: Allowed mentions for the message.
            reply_to: Message to reference, must be from the same channel.
            files: Files to send, the path, bytes or File() instance, defaults to None. You may have up to 10 files.
            file: Files to send, the path, bytes or File() instance, defaults to None. You may have up to 10 files.
            tts: Should this message use Text To Speech.
            suppress_embeds: Should embeds be suppressed on this send
            silent: Should this message be sent without triggering a notification.
            flags: Message flags to apply.
            delete_after: Delete message after this many seconds.
            ephemeral: Whether the response should be ephemeral

        Returns:
            New message object that was sent.
        """
        flags = MessageFlags(flags or 0)
        if ephemeral:
            flags |= MessageFlags.EPHEMERAL
            self.ephemeral = True
        if suppress_embeds:
            flags |= MessageFlags.SUPPRESS_EMBEDS
        if silent:
            flags |= MessageFlags.SILENT

        return await super().send(
            content=content,
            embeds=embeds,
            embed=embed,
            components=components,
            stickers=stickers,
            allowed_mentions=allowed_mentions,
            reply_to=reply_to,
            files=files,
            file=file,
            tts=tts,
            flags=flags,
            delete_after=delete_after,
            pass_self_into_delete=True,
            **kwargs,
        )

    respond = send

    async def delete(self, message: "Snowflake_Type") -> None:
        """
        Delete a message sent in response to this interaction.

        Args:
            message: The message to delete
        """
        await self.client.http.delete_interaction_message(self.client.app.id, self.token, to_snowflake(message))

    async def edit(
        self,
        message: "Snowflake_Type",
        *,
        content: typing.Optional[str] = None,
        embeds: typing.Optional[
            typing.Union[typing.Iterable[typing.Union["Embed", dict]], typing.Union["Embed", dict]]
        ] = None,
        embed: typing.Optional[typing.Union["Embed", dict]] = None,
        components: typing.Optional[
            typing.Union[
                typing.Iterable[typing.Iterable[typing.Union["BaseComponent", dict]]],
                typing.Iterable[typing.Union["BaseComponent", dict]],
                "BaseComponent",
                dict,
            ]
        ] = None,
        attachments: typing.Optional[typing.Sequence[Attachment | dict]] = None,
        allowed_mentions: typing.Optional[typing.Union["AllowedMentions", dict]] = None,
        files: typing.Optional[typing.Union["UPLOADABLE_TYPE", typing.Iterable["UPLOADABLE_TYPE"]]] = None,
        file: typing.Optional["UPLOADABLE_TYPE"] = None,
        tts: bool = False,
    ) -> "interactions.Message":
        message_payload = process_message_payload(
            content=content,
            embeds=embeds or embed,
            components=components,
            allowed_mentions=allowed_mentions,
            attachments=attachments,
            tts=tts,
        )

        if file:
            files = [file, *files] if files else [file]
        message_data = await self.client.http.edit_interaction_message(
            payload=message_payload,
            application_id=self.client.app.id,
            token=self.token,
            message_id=to_snowflake(message),
            files=files,
        )
        if message_data:
            return self.client.cache.place_message_data(message_data)


class SlashContext(InteractionContext, ModalMixin):
    @classmethod
    def from_dict(cls, client: "interactions.Client", payload: dict) -> Self:
        return super().from_dict(client, payload)


class ContextMenuContext(InteractionContext, ModalMixin):
    target_id: Snowflake
    """The id of the target of the context menu."""
    editing_origin: bool
    """Whether you have deferred the interaction and are editing the original response."""
    target_type: None | CommandType
    """The type of the target of the context menu."""

    def __init__(self, client: "interactions.Client") -> None:
        super().__init__(client)
        self.editing_origin = False

    @classmethod
    def from_dict(cls, client: "interactions.Client", payload: dict) -> Self:
        instance = super().from_dict(client, payload)
        instance.target_id = Snowflake(payload["data"]["target_id"])
        instance.target_type = CommandType(payload["data"]["type"])
        return instance

    async def defer(self, *, ephemeral: bool = False, edit_origin: bool = False) -> None:
        """
        Defer the interaction.

        Args:
            ephemeral: Whether the interaction response should be ephemeral.
            edit_origin: Whether to edit the original message instead of sending a new one.
        """
        if self.deferred:
            raise AlreadyDeferred("Interaction has already been responded to.")
        if self.responded:
            raise AlreadyResponded("Interaction has already been responded to.")

        payload = {
            "type": CallbackType.DEFERRED_UPDATE_MESSAGE
            if edit_origin
            else CallbackType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE
        }
        if ephemeral:
            if edit_origin:
                raise ValueError("Cannot use ephemeral and edit_origin together.")
            payload["data"] = {"flags": MessageFlags.EPHEMERAL}

        await self.client.http.post_initial_response(payload, self.id, self.token)
        self.deferred = True
        self.ephemeral = ephemeral
        self.editing_origin = edit_origin

    @property
    def target(self) -> None | Message | User | Member:
        """
        The target of the context menu.

        Returns:
            The target of the context menu.
        """
        return self.resolved.get(self.target_id)


class ComponentContext(InteractionContext, ModalMixin):
    values: list[str]
    """The values of the SelectMenu component, if any."""
    custom_id: str
    """The custom_id of the component."""
    component_type: int
    """The type of the component."""
    defer_edit_origin: bool
    """Whether you have deferred the interaction and are editing the original response."""

    @classmethod
    def from_dict(cls, client: "interactions.Client", payload: dict) -> Self:
        instance = super().from_dict(client, payload)
        instance.values = payload["data"].get("values", [])
        instance.custom_id = payload["data"]["custom_id"]
        instance._command_id = instance.custom_id
        instance._command_name = instance.custom_id
        instance.component_type = payload["data"]["component_type"]
        instance.defer_edit_origin = False

        searches = {
            "users": instance.component_type in (ComponentType.USER_SELECT, ComponentType.MENTIONABLE_SELECT),
            "members": instance.guild_id
            and instance.component_type in (ComponentType.USER_SELECT, ComponentType.MENTIONABLE_SELECT),
            "channels": instance.component_type in (ComponentType.CHANNEL_SELECT, ComponentType.MENTIONABLE_SELECT),
            "roles": instance.guild_id
            and instance.component_type in (ComponentType.ROLE_SELECT, ComponentType.MENTIONABLE_SELECT),
        }

        if instance.component_type in (
            ComponentType.USER_SELECT,
            ComponentType.CHANNEL_SELECT,
            ComponentType.ROLE_SELECT,
            ComponentType.MENTIONABLE_SELECT,
        ):
            for i, value in enumerate(instance.values):
                if re.match(r"\d{17,}", value):
                    key = Snowflake(value)

                    if resolved := instance.resolved.get(key):
                        instance.values[i] = resolved
                    elif searches["members"] and (member := instance.client.cache.get_member(instance.guild_id, key)):
                        instance.values[i] = member
                    elif searches["users"] and (user := instance.client.cache.get_user(key)):
                        instance.values[i] = user
                    elif searches["roles"] and (role := instance.client.cache.get_role(key)):
                        instance.values[i] = role
                    elif searches["channels"] and (channel := instance.client.cache.get_channel(key)):
                        instance.values[i] = channel
        return instance

    async def defer(self, *, ephemeral: bool = False, edit_origin: bool = False) -> None:
        """
        Defer the interaction.

        Args:
            ephemeral: Whether the interaction response should be ephemeral.
            edit_origin: Whether to edit the original message instead of sending a new one.
        """
        if self.deferred:
            raise AlreadyDeferred("Interaction has already been responded to.")
        if self.responded:
            raise AlreadyResponded("Interaction has already been responded to.")

        payload = {
            "type": CallbackType.DEFERRED_UPDATE_MESSAGE
            if edit_origin
            else CallbackType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE
        }
        if ephemeral:
            if edit_origin:
                raise ValueError("Cannot use ephemeral and edit_origin together.")
            payload["data"] = {"flags": MessageFlags.EPHEMERAL}

        await self.client.http.post_initial_response(payload, self.id, self.token)
        self.deferred = True
        self.ephemeral = ephemeral
        self.editing_origin = edit_origin

    async def edit_origin(
        self,
        *,
        content: typing.Optional[str] = None,
        embeds: typing.Optional[
            typing.Union[typing.Iterable[typing.Union["Embed", dict]], typing.Union["Embed", dict]]
        ] = None,
        embed: typing.Optional[typing.Union["Embed", dict]] = None,
        components: typing.Optional[
            typing.Union[
                typing.Iterable[typing.Iterable[typing.Union["BaseComponent", dict]]],
                typing.Iterable[typing.Union["BaseComponent", dict]],
                "BaseComponent",
                dict,
            ]
        ] = None,
        allowed_mentions: typing.Optional[typing.Union["AllowedMentions", dict]] = None,
        files: typing.Optional[typing.Union["UPLOADABLE_TYPE", typing.Iterable["UPLOADABLE_TYPE"]]] = None,
        file: typing.Optional["UPLOADABLE_TYPE"] = None,
        tts: bool = False,
    ) -> "Message":
        """
        Edits the original message of the component.

        Args:
            content: Message text content.
            embeds: Embedded rich content (up to 6000 characters).
            embed: Embedded rich content (up to 6000 characters).
            components: The components to include with the message.
            allowed_mentions: Allowed mentions for the message.
            files: Files to send, the path, bytes or File() instance, defaults to None. You may have up to 10 files.
            file: Files to send, the path, bytes or File() instance, defaults to None. You may have up to 10 files.
            tts: Should this message use Text To Speech.

        Returns:
            The message after it was edited.
        """
        if not self.responded and not self.deferred and (files or file):
            # Discord doesn't allow files at initial response, so we defer then edit.
            await self.defer(edit_origin=True)

        message_payload = process_message_payload(
            content=content,
            embeds=embeds or embed,
            components=components,
            allowed_mentions=allowed_mentions,
            tts=tts,
        )

        message_data = None
        if self.deferred:
            if not self.editing_origin:
                get_logger().warning(
                    "If you want to edit the original message, and need to defer, you must set the `edit_origin` kwarg to True!"
                )

            message_data = await self.client.http.edit_interaction_message(
                message_payload, self.client.app.id, self.token, files=files or file
            )
            self.deferred = False
            self.editing_origin = False
        else:
            payload = {"type": CallbackType.UPDATE_MESSAGE, "data": message_payload}
            await self.client.http.post_initial_response(payload, str(self.id), self.token, files=files or file)
            message_data = await self.client.http.get_interaction_message(self.client.app.id, self.token)

        if message_data:
            message = self.client.cache.place_message_data(message_data)
            self.message_id = message.id
            return message

    @property
    def component(self) -> typing.Optional[BaseComponent]:
        """The component that was interacted with."""
        if self.message is None or self.message.components is None:
            return None
        for action_row in self.message.components:
            for component in action_row.components:
                if component.custom_id == self.custom_id:
                    return component


class ModalContext(InteractionContext):
    responses: dict[str, str]
    """The responses of the modal. The key is the `custom_id` of the component."""
    custom_id: str
    """The developer defined custom ID of this modal"""
    edit_origin: bool
    """Whether to edit the original message instead of sending a new one."""

    @classmethod
    def from_dict(cls, client: "interactions.Client", payload: dict) -> Self:
        instance = super().from_dict(client, payload)
        instance.responses = {
            comp["components"][0]["custom_id"]: comp["components"][0]["value"] for comp in payload["data"]["components"]
        }
        instance.kwargs = instance.responses
        instance.custom_id = payload["data"]["custom_id"]
        instance.edit_origin = False
        return instance

    async def edit(self, message: "Snowflake_Type", **kwargs) -> "interactions.Message":
        if not self.deferred and not self.responded:
            await self.defer(edit_origin=True)
        return await super().edit(message, **kwargs)

    async def defer(self, *, ephemeral: bool = False, edit_origin: bool = False) -> None:
        """
        Defer the interaction.

        Args:
            ephemeral: Whether the interaction response should be ephemeral.
            edit_origin: Whether to edit the original message instead of sending a followup.
        """
        if self.deferred:
            raise AlreadyDeferred("Interaction has already been responded to.")
        if self.responded:
            raise AlreadyResponded("Interaction has already been responded to.")

        payload = {
            "type": CallbackType.DEFERRED_UPDATE_MESSAGE
            if edit_origin
            else CallbackType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE
        }
        if ephemeral:
            payload["data"] = {"flags": MessageFlags.EPHEMERAL}

        if edit_origin:
            self.edit_origin = True

        await self.client.http.post_initial_response(payload, self.id, self.token)
        self.deferred = True
        self.ephemeral = ephemeral


class AutocompleteContext(BaseInteractionContext):
    focussed_option: SlashCommandOption  # todo: option parsing
    """The option the user is currently filling in."""

    @classmethod
    def from_dict(cls, client: "interactions.Client", payload: dict) -> Self:
        return super().from_dict(client, payload)

    @property
    def input_text(self) -> str:
        """The text the user has already filled in."""
        return self.kwargs.get(str(self.focussed_option.name), "")

    def option_processing_hook(self, option: dict) -> None:
        if option.get("focused", False):
            self.focussed_option = SlashCommandOption.from_dict(option)
        return

    async def send(
        self, choices: typing.Iterable[str | int | float | dict[str, int | float | str] | SlashCommandChoice]
    ) -> None:
        """
        Send your autocomplete choices to discord. Choices must be either a list of strings, or a dictionary following the following format:

        ```json
            {
              "name": str,
              "value": str
            }
        ```
        Where name is the text visible in Discord, and value is the data sent back to your client when that choice is
        chosen.

        Args:
            choices: 25 choices the user can pick
        """
        if self.focussed_option.type == OptionType.STRING:
            type_cast = str
        elif self.focussed_option.type == OptionType.INTEGER:
            type_cast = int
        elif self.focussed_option.type == OptionType.NUMBER:
            type_cast = float
        else:
            type_cast = None

        processed_choices = []
        for choice in choices:
            if isinstance(choice, dict):
                name = choice["name"]
                value = choice["value"]
            elif isinstance(choice, SlashCommandChoice):
                name = choice.name.get_locale(self.locale)
                value = choice.value
            else:
                name = str(choice)
                value = choice

            processed_choices.append({"name": name, "value": type_cast(value) if type_cast else value})

        payload = {"type": CallbackType.AUTOCOMPLETE_RESULT, "data": {"choices": processed_choices}}
        await self.client.http.post_initial_response(payload, self.id, self.token)
