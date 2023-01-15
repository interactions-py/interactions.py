import datetime
from logging import Logger
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Protocol, Union, runtime_checkable, Sequence

import attrs
from aiohttp import FormData

import interactions.models as models
import interactions.models.discord.message as message
from interactions.client.const import Absent, MISSING, get_logger
from interactions.client.errors import AlreadyDeferred
from interactions.client.mixins.send import SendMixin
from interactions.client.utils.attr_converters import optional
from interactions.client.utils.attr_utils import docs
from interactions.models.discord.enums import MessageFlags, CommandTypes, Permissions
from interactions.models.discord.file import UPLOADABLE_TYPE
from interactions.models.discord.message import Attachment
from interactions.models.discord.snowflake import to_snowflake, to_optional_snowflake
from interactions.models.discord.timestamp import Timestamp
from interactions.models.internal.application_commands import CallbackTypes, OptionTypes

if TYPE_CHECKING:
    from io import IOBase
    from pathlib import Path

    from interactions.client import Client
    from interactions.models.discord.channel import TYPE_MESSAGEABLE_CHANNEL
    from interactions.models.discord.components import BaseComponent
    from interactions.models.discord.embed import Embed
    from interactions.models.discord.file import File
    from interactions.models.discord.guild import Guild
    from interactions.models.discord.message import AllowedMentions, Message
    from interactions.models.discord.user import User, Member
    from interactions.models.discord.snowflake import Snowflake_Type
    from interactions.models.discord.message import MessageReference
    from interactions.models.discord.sticker import Sticker
    from interactions.models.discord.role import Role
    from interactions.models.discord.modal import Modal
    from interactions.models.internal.active_voice_state import ActiveVoiceState
    from interactions.models.internal.command import BaseCommand

__all__ = (
    "Resolved",
    "Context",
    "InteractionContext",
    "ComponentContext",
    "AutocompleteContext",
    "ModalContext",
    "PrefixedContext",
    "HybridContext",
    "SendableContext",
)


@attrs.define(eq=False, order=False, hash=False, kw_only=True)
class Resolved:
    """Represents resolved data in an interaction."""

    channels: Dict["Snowflake_Type", "TYPE_MESSAGEABLE_CHANNEL"] = attrs.field(
        repr=False, factory=dict, metadata=docs("A dictionary of channels mentioned in the interaction")
    )
    members: Dict["Snowflake_Type", "Member"] = attrs.field(
        repr=False, factory=dict, metadata=docs("A dictionary of members mentioned in the interaction")
    )
    users: Dict["Snowflake_Type", "User"] = attrs.field(
        repr=False, factory=dict, metadata=docs("A dictionary of users mentioned in the interaction")
    )
    roles: Dict["Snowflake_Type", "Role"] = attrs.field(
        repr=False, factory=dict, metadata=docs("A dictionary of roles mentioned in the interaction")
    )
    messages: Dict["Snowflake_Type", "Message"] = attrs.field(
        repr=False, factory=dict, metadata=docs("A dictionary of messages mentioned in the interaction")
    )
    attachments: Dict["Snowflake_Type", "Attachment"] = attrs.field(
        repr=False, factory=dict, metadata=docs("A dictionary of attachments tied to the interaction")
    )

    @classmethod
    def from_dict(cls, client: "Client", data: dict, guild_id: Optional["Snowflake_Type"] = None) -> "Resolved":
        new_cls = cls()

        if channels := data.get("channels"):
            for key, _channel in channels.items():
                new_cls.channels[key] = client.cache.place_channel_data(_channel)

        if members := data.get("members"):
            for key, _member in members.items():
                new_cls.members[key] = client.cache.place_member_data(
                    guild_id, {**_member, "user": {**data["users"][key]}}
                )

        if users := data.get("users"):
            for key, _user in users.items():
                new_cls.users[key] = client.cache.place_user_data(_user)

        if roles := data.get("roles"):
            for key, _role in roles.items():
                new_cls.roles[key] = client.cache.get_role(to_snowflake(key))

        if messages := data.get("messages"):
            for key, _msg in messages.items():
                new_cls.messages[key] = client.cache.place_message_data(_msg)

        if attachments := data.get("attachments"):
            for key, _attach in attachments.items():
                new_cls.attachments[key] = Attachment.from_dict(_attach, client)

        return new_cls


@attrs.define(eq=False, order=False, hash=False, kw_only=True)
class Context:
    """Represents the context of a command."""

    _client: "Client" = attrs.field(repr=False, default=None)
    invoke_target: str = attrs.field(repr=False, default=None, metadata=docs("The name of the command to be invoked"))
    command: Optional["BaseCommand"] = attrs.field(repr=False, default=None, metadata=docs("The command to be invoked"))

    args: List = attrs.field(
        repr=False, factory=list, metadata=docs("The list of arguments to be passed to the command")
    )
    kwargs: Dict = attrs.field(repr=False, factory=dict, metadata=docs("The list of keyword arguments to be passed"))

    author: Union["Member", "User"] = attrs.field(repr=False, default=None, metadata=docs("The author of the message"))
    channel: "TYPE_MESSAGEABLE_CHANNEL" = attrs.field(
        repr=False, default=None, metadata=docs("The channel this was sent within")
    )
    guild_id: "Snowflake_Type" = attrs.field(
        repr=False,
        default=None,
        converter=to_optional_snowflake,
        metadata=docs("The guild this was sent within, if not a DM"),
    )
    message: "Message" = attrs.field(
        repr=False, default=None, metadata=docs("The message associated with this context")
    )

    logger: Logger = attrs.field(repr=False, init=False, factory=get_logger)

    @property
    def guild(self) -> Optional["Guild"]:
        return self._client.cache.get_guild(self.guild_id)

    @property
    def bot(self) -> "Client":
        """A reference to the bot instance."""
        return self._client

    @property
    def voice_state(self) -> Optional["ActiveVoiceState"]:
        return self._client.cache.get_bot_voice_state(self.guild_id)


@attrs.define(eq=False, order=False, hash=False, kw_only=True)
class _BaseInteractionContext(Context):
    """An internal object used to define the attributes of interaction context and its children."""

    _token: str = attrs.field(repr=False, default=None, metadata=docs("The token for the interaction"))
    _context_type: int = attrs.field(
        repr=False,
    )  # we don't want to convert this in case of a new context type, which is expected
    interaction_id: "Snowflake_Type" = attrs.field(
        repr=False, default=None, metadata=docs("The id of the interaction"), converter=to_snowflake
    )
    target_id: "Snowflake_Type" = attrs.field(
        default=None,
        metadata=docs("The ID of the target, used for context menus to show what was clicked on"),
        converter=optional(to_snowflake),
    )
    app_permissions: Permissions = attrs.field(
        repr=False, default=0, converter=Permissions, metadata=docs("The permissions this interaction has")
    )
    locale: str = attrs.field(
        default=None,
        metadata=docs(
            "The selected language of the invoking user \n(https://discord.com/developers/docs/reference#locales)"
        ),
    )
    guild_locale: str = attrs.field(repr=False, default=None, metadata=docs("The guild's preferred locale"))

    deferred: bool = attrs.field(repr=False, default=False, metadata=docs("Is this interaction deferred?"))
    responded: bool = attrs.field(repr=False, default=False, metadata=docs("Have we responded to the interaction?"))
    ephemeral: bool = attrs.field(
        repr=False, default=False, metadata=docs("Are responses to this interaction *hidden*")
    )

    resolved: Resolved = attrs.field(
        repr=False, default=Resolved(), metadata=docs("Discord objects mentioned within this interaction")
    )

    data: Dict = attrs.field(repr=False, factory=dict, metadata=docs("The raw data of this interaction"))

    @classmethod
    def from_dict(cls, data: Dict, client: "Client") -> "Context":
        """Create a context object from a dictionary."""
        new_cls = cls(
            client=client,
            token=data["token"],
            interaction_id=data["id"],
            data=data,
            invoke_target=data["data"].get("name"),
            guild_id=data.get("guild_id"),
            context_type=data["data"].get("type", 0),
            locale=data.get("locale"),
            guild_locale=data.get("guild_locale"),
            app_permissions=data.get("app_permissions", 0),
        )
        new_cls.data = data

        if res_data := data["data"].get("resolved"):
            new_cls.resolved = Resolved.from_dict(client, res_data, new_cls.guild_id)

        if new_cls.guild_id:
            new_cls.author = client.cache.place_member_data(new_cls.guild_id, data["member"].copy())
            client.cache.place_user_data(data["member"]["user"])
            new_cls.channel = client.cache.get_channel(to_snowflake(data["channel_id"]))
        else:
            new_cls.author = client.cache.place_user_data(data["user"])
            new_cls.channel = client.cache.get_channel(new_cls.author.id)

        new_cls.target_id = data["data"].get("target_id")

        new_cls._process_options(data)

        return new_cls

    def _process_options(self, data: dict) -> None:
        kwargs = {}
        guild_id = to_snowflake(data.get("guild_id", 0))
        if options := data["data"].get("options"):
            o_type = options[0]["type"]
            if o_type in (OptionTypes.SUB_COMMAND, OptionTypes.SUB_COMMAND_GROUP):
                # this is a subcommand, process accordingly
                if o_type == OptionTypes.SUB_COMMAND:
                    self.invoke_target = f"{self.invoke_target} {options[0]['name']}"
                    options = options[0].get("options", [])
                else:
                    self.invoke_target = (
                        f"{self.invoke_target} {options[0]['name']} "
                        f"{next(x for x in options[0]['options'] if x['type'] == OptionTypes.SUB_COMMAND)['name']}"
                    )
                    options = options[0]["options"][0].get("options", [])
            for option in options:
                value = option.get("value")

                # this block here resolves the options using the cache
                match option["type"]:
                    case OptionTypes.USER:
                        value = (
                            self._client.cache.get_member(guild_id, to_snowflake(value))
                            or self._client.cache.get_user(to_snowflake(value))
                        ) or value

                    case OptionTypes.CHANNEL:
                        value = self._client.cache.get_channel(to_snowflake(value)) or value

                    case OptionTypes.ROLE:
                        value = self._client.cache.get_role(to_snowflake(value)) or value

                    case OptionTypes.MENTIONABLE:
                        snow = to_snowflake(value)
                        if user := self._client.cache.get_member(guild_id, snow) or self._client.cache.get_user(snow):
                            value = user
                        elif role := self._client.cache.get_role(snow):
                            value = role

                    case OptionTypes.ATTACHMENT:
                        value = self.resolved.attachments.get(value)

                if option.get("focused", False):
                    self.focussed_option = option.get("name")
                kwargs[option["name"].lower()] = value
        self.kwargs = kwargs
        self.args = list(kwargs.values())

    @property
    def expires_at(self) -> Timestamp:
        """The timestamp the interaction is expected to expire at."""
        if self.responded:
            return Timestamp.from_snowflake(self.interaction_id) + datetime.timedelta(minutes=15)
        return Timestamp.from_snowflake(self.interaction_id) + datetime.timedelta(seconds=3)

    @property
    def expired(self) -> bool:
        """Has the interaction expired yet?"""
        return Timestamp.utcnow() >= self.expires_at

    @property
    def invoked_name(self) -> str:
        return self.command.get_localised_name(self.locale)

    async def send_modal(self, modal: Union[dict, "Modal"]) -> Union[dict, "Modal"]:
        """
        Respond using a modal.

        Args:
            modal: The modal to respond with

        Returns:
            The modal used.

        """
        payload = modal.to_dict() if not isinstance(modal, dict) else modal

        await self._client.http.post_initial_response(payload, self.interaction_id, self._token)

        self.responded = True
        return modal


@attrs.define(eq=False, order=False, hash=False, kw_only=True)
class InteractionContext(_BaseInteractionContext, SendMixin):
    """
    Represents the context of an interaction.

    !!! info "Ephemeral messages:"
        Ephemeral messages allow you to send messages that only the author of the interaction can see.
        They are best considered as `fire-and-forget`, in the sense that you cannot edit them once they have been sent.

        Should you attach a component (ie. button) to the ephemeral message,
        you will be able to edit it when responding to a button interaction.

    """

    async def defer(self, ephemeral: bool = False) -> None:
        """
        Defers the response, showing a loading state.

        Args:
            ephemeral: Should the response be ephemeral

        """
        if self.deferred or self.responded:
            raise AlreadyDeferred("You have already responded to this interaction!")

        payload = {"type": CallbackTypes.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE}
        if ephemeral:
            payload["data"] = {"flags": MessageFlags.EPHEMERAL}

        await self._client.http.post_initial_response(payload, self.interaction_id, self._token)
        self.ephemeral = ephemeral
        self.deferred = True

    async def _send_http_request(
        self, message_payload: Union[dict, "FormData"], files: Iterable["UPLOADABLE_TYPE"] | None = None
    ) -> dict:
        if self.responded:
            message_data = await self._client.http.post_followup(
                message_payload, self._client.app.id, self._token, files=files
            )
        else:
            if isinstance(message_payload, FormData) and not self.deferred:
                await self.defer(self.ephemeral)
            if self.deferred:
                message_data = await self._client.http.edit_interaction_message(
                    message_payload, self._client.app.id, self._token, files=files
                )
                self.deferred = False
            else:
                payload = {"type": CallbackTypes.CHANNEL_MESSAGE_WITH_SOURCE, "data": message_payload}
                await self._client.http.post_initial_response(payload, self.interaction_id, self._token, files=files)
                message_data = await self._client.http.get_interaction_message(self._client.app.id, self._token)
            self.responded = True

        return message_data

    async def send(
        self,
        content: Optional[str] = None,
        *,
        embeds: Optional[Union[Iterable[Union["Embed", dict]], Union["Embed", dict]]] = None,
        embed: Optional[Union["Embed", dict]] = None,
        components: Optional[
            Union[
                Iterable[Iterable[Union["BaseComponent", dict]]],
                Iterable[Union["BaseComponent", dict]],
                "BaseComponent",
                dict,
            ]
        ] = None,
        stickers: Optional[Union[Iterable[Union["Sticker", "Snowflake_Type"]], "Sticker", "Snowflake_Type"]] = None,
        allowed_mentions: Optional[Union["AllowedMentions", dict]] = None,
        reply_to: Optional[Union["MessageReference", "Message", dict, "Snowflake_Type"]] = None,
        files: Optional[Union[UPLOADABLE_TYPE, Iterable[UPLOADABLE_TYPE]]] = None,
        file: Optional[UPLOADABLE_TYPE] = None,
        tts: bool = False,
        suppress_embeds: bool = False,
        flags: Optional[Union[int, "MessageFlags"]] = None,
        ephemeral: bool = False,
    ) -> "Message":
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
            flags: Message flags to apply.
            ephemeral bool: Should this message be sent as ephemeral (hidden)

        Returns:
            New message object that was sent.

        """
        if ephemeral:
            flags = MessageFlags.EPHEMERAL
            self.ephemeral = True

        if suppress_embeds:
            if isinstance(flags, int):
                flags = MessageFlags(flags)
            flags = flags | MessageFlags.SUPPRESS_EMBEDS

        return await super().send(
            content,
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
        )

    async def delete(self, message: "Snowflake_Type") -> None:
        """
        Delete a message sent in response to this interaction.

        Args:
            message: The message to delete

        """
        await self._client.http.delete_interaction_message(self._client.app.id, self._token, to_snowflake(message))

    async def edit(
        self,
        message: "Snowflake_Type",
        *,
        content: Optional[str] = None,
        embeds: Optional[Union[Sequence[Union["models.Embed", dict]], Union["models.Embed", dict]]] = None,
        embed: Optional[Union["models.Embed", dict]] = None,
        components: Optional[
            Union[
                Sequence[Sequence[Union["models.BaseComponent", dict]]],
                Sequence[Union["models.BaseComponent", dict]],
                "models.BaseComponent",
                dict,
            ]
        ] = None,
        allowed_mentions: Optional[Union["models.AllowedMentions", dict]] = None,
        attachments: Optional[Optional[Sequence[Union[Attachment, dict]]]] = None,
        files: Optional[Union[UPLOADABLE_TYPE, Sequence[UPLOADABLE_TYPE]]] = None,
        file: Optional[UPLOADABLE_TYPE] = None,
        tts: bool = False,
    ) -> "models.Message":
        message_payload = models.process_message_payload(
            content=content,
            embeds=embeds or embed,
            components=components,
            allowed_mentions=allowed_mentions,
            attachments=attachments,
            tts=tts,
        )

        if file:
            if files:
                files = [file, *files]
            else:
                files = [file]

        message_data = await self._client.http.edit_interaction_message(
            payload=message_payload,
            application_id=self._client.app.id,
            token=self._token,
            message_id=to_snowflake(message),
            files=files,
        )
        if message_data:
            return self._client.cache.place_message_data(message_data)

    @property
    def target(self) -> "Absent[Member | User | Message]":
        """For context menus, this will be the object of which was clicked on."""
        thing = MISSING

        match self._context_type:
            # Only searches caches based on what kind of context menu this is

            case CommandTypes.USER:
                # This can only be in the member or user cache
                caches = (
                    (self._client.cache.get_member, (self.guild_id, self.target_id)),
                    (self._client.cache.get_user, (self.target_id,)),
                )
            case CommandTypes.MESSAGE:
                # This can only be in the message cache
                caches = ((self._client.cache.get_message, (self.channel.id, self.target_id)),)
            case _:
                # Most likely a new context type, check all rational caches for the target_id
                self.logger.warning(f"New Context Type Detected. Please Report: {self._context_type}")
                caches = (
                    (self._client.cache.get_message, (self.channel.id, self.target_id)),
                    (self._client.cache.get_member, (self.guild_id, self.target_id)),
                    (self._client.cache.get_user, (self.target_id,)),
                    (self._client.cache.get_channel, (self.target_id,)),
                    (self._client.cache.get_role, (self.target_id,)),
                    (self._client.cache.get_emoji, (self.target_id,)),  # unlikely, so check last
                )

        for cache, keys in caches:
            thing = cache(*keys)
            if thing is not None:
                break
        return thing


@attrs.define(eq=False, order=False, hash=False, kw_only=True)
class ComponentContext(InteractionContext):
    custom_id: str = attrs.field(
        repr=False, default="", metadata=docs("The ID given to the component that has been pressed")
    )
    component_type: int = attrs.field(
        repr=False, default=0, metadata=docs("The type of component that has been pressed")
    )

    values: List = attrs.field(repr=False, factory=list, metadata=docs("The values set"))

    defer_edit_origin: bool = attrs.field(
        repr=False, default=False, metadata=docs("Are we editing the message the component is on")
    )

    @classmethod
    def from_dict(cls, data: Dict, client: "Client") -> "ComponentContext":
        """Create a context object from a dictionary."""
        new_cls = super().from_dict(data, client)
        new_cls.token = data["token"]
        new_cls.interaction_id = data["id"]
        new_cls.invoke_target = data["data"]["custom_id"]
        new_cls.custom_id = data["data"]["custom_id"]
        new_cls.component_type = data["data"]["component_type"]
        new_cls.message = client.cache.place_message_data(data["message"])
        new_cls.values = data["data"].get("values", [])

        return new_cls

    async def defer(self, ephemeral: bool = False, edit_origin: bool = False) -> None:
        """
        Defers the response, showing a loading state.

        Args:
            ephemeral: Should the response be ephemeral
            edit_origin: Whether we intend to edit the original message

        """
        if self.deferred or self.responded:
            raise AlreadyDeferred("You have already responded to this interaction!")

        payload = {
            "type": CallbackTypes.DEFERRED_UPDATE_MESSAGE
            if edit_origin
            else CallbackTypes.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE
        }

        if ephemeral:
            if edit_origin:
                raise ValueError("`edit_origin` and `ephemeral` are mutually exclusive")
            payload["data"] = {"flags": MessageFlags.EPHEMERAL}

        await self._client.http.post_initial_response(payload, self.interaction_id, self._token)
        self.deferred = True
        self.ephemeral = ephemeral
        self.defer_edit_origin = edit_origin

    async def edit_origin(
        self,
        *,
        content: str = None,
        embeds: Optional[Union[Iterable[Union["Embed", dict]], Union["Embed", dict]]] = None,
        embed: Optional[Union["Embed", dict]] = None,
        components: Optional[
            Union[
                Iterable[Iterable[Union["BaseComponent", dict]]],
                Iterable[Union["BaseComponent", dict]],
                "BaseComponent",
                dict,
            ]
        ] = None,
        allowed_mentions: Optional[Union["AllowedMentions", dict]] = None,
        files: Optional[Union[UPLOADABLE_TYPE, Iterable[UPLOADABLE_TYPE]]] = None,
        file: Optional[UPLOADABLE_TYPE] = None,
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

        message_payload = message.process_message_payload(
            content=content,
            embeds=embeds or embed,
            components=components,
            allowed_mentions=allowed_mentions,
            tts=tts,
        )

        message_data = None
        if self.deferred:
            if not self.defer_edit_origin:
                self.logger.warning(
                    "If you want to edit the original message, and need to defer, you must set the `edit_origin` kwarg to True!"
                )

            message_data = await self._client.http.edit_interaction_message(
                message_payload, self._client.app.id, self._token
            )
            self.deferred = False
            self.defer_edit_origin = False
        else:
            payload = {"type": CallbackTypes.UPDATE_MESSAGE, "data": message_payload}
            await self._client.http.post_initial_response(
                payload, self.interaction_id, self._token, files=files or file
            )
            message_data = await self._client.http.get_interaction_message(self._client.app.id, self._token)

        if message_data:
            self.message = self._client.cache.place_message_data(message_data)
            return self.message


@attrs.define(eq=False, order=False, hash=False, kw_only=True)
class AutocompleteContext(_BaseInteractionContext):
    focussed_option: str = attrs.field(
        repr=False, default=MISSING, metadata=docs("The option the user is currently filling in")
    )

    @classmethod
    def from_dict(cls, data: Dict, client: "Client") -> "ComponentContext":
        """Create a context object from a dictionary."""
        new_cls = super().from_dict(data, client)

        return new_cls

    @property
    def input_text(self) -> str:
        """The text the user has entered so far."""
        return self.kwargs.get(self.focussed_option, "")

    async def send(self, choices: Iterable[Union[str, int, float, Dict[str, Union[str, int, float]]]]) -> None:
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
        processed_choices = []
        for choice in choices:
            if isinstance(choice, (int, float)):
                processed_choices.append({"name": str(choice), "value": choice})
            elif isinstance(choice, dict):
                processed_choices.append(choice)
            else:
                choice = str(choice)
                processed_choices.append({"name": choice, "value": choice.replace(" ", "_")})

        payload = {"type": CallbackTypes.AUTOCOMPLETE_RESULT, "data": {"choices": processed_choices}}
        await self._client.http.post_initial_response(payload, self.interaction_id, self._token)


@attrs.define(eq=False, order=False, hash=False, kw_only=True)
class ModalContext(InteractionContext):
    custom_id: str = attrs.field(repr=False, default="")

    @classmethod
    def from_dict(cls, data: Dict, client: "Client") -> "ModalContext":
        new_cls = super().from_dict(data, client)

        new_cls.kwargs = {
            comp["components"][0]["custom_id"]: comp["components"][0]["value"] for comp in data["data"]["components"]
        }
        new_cls.custom_id = data["data"]["custom_id"]
        return new_cls

    @property
    def responses(self) -> dict[str, str]:
        """
        Get the responses to this modal.

        Returns:
            A dictionary of responses. Keys are the custom_ids of your components.
        """
        return self.kwargs


@attrs.define(eq=False, order=False, hash=False, kw_only=True)
class PrefixedContext(Context, SendMixin):
    prefix: str = attrs.field(repr=False, default=MISSING, metadata=docs("The prefix used to invoke this command"))

    @classmethod
    def from_message(cls, client: "Client", message: "Message") -> "PrefixedContext":
        new_cls = cls(
            client=client,
            message=message,
            author=message.author,
            channel=message.channel,
            guild_id=message._guild_id,
        )
        return new_cls

    @property
    def content_parameters(self) -> str:
        return self.message.content.removeprefix(f"{self.prefix}{self.invoke_target}").strip()

    async def reply(
        self,
        content: Optional[str] = None,
        embeds: Optional[Union[Iterable[Union["Embed", dict]], Union["Embed", dict]]] = None,
        embed: Optional[Union["Embed", dict]] = None,
        **kwargs,
    ) -> "Message":
        """Reply to this message, takes all the same attributes as `send`."""
        return await self.send(content=content, reply_to=self.message, embeds=embeds or embed, **kwargs)

    async def _send_http_request(
        self, message_payload: Union[dict, "FormData"], files: Iterable["UPLOADABLE_TYPE"] | None = None
    ) -> dict:
        return await self._client.http.create_message(message_payload, self.channel.id, files=files)


@attrs.define(eq=False, order=False, hash=False, kw_only=True)
class HybridContext(Context):
    """
    Represents the context for hybrid commands, a slash command that can also be used as a prefixed command.

    This attempts to create a compatibility layer to allow contexts for an interaction or a message to be used seamlessly.
    """

    deferred: bool = attrs.field(repr=False, default=False, metadata=docs("Is this context deferred?"))
    responded: bool = attrs.field(repr=False, default=False, metadata=docs("Have we responded to this?"))
    app_permissions: Permissions = attrs.field(
        repr=False, default=0, converter=Permissions, metadata=docs("The permissions this context has")
    )

    _interaction_context: Optional[InteractionContext] = attrs.field(repr=False, default=None)
    _prefixed_context: Optional[PrefixedContext] = attrs.field(repr=False, default=None)

    @classmethod
    def from_interaction_context(cls, context: InteractionContext) -> "HybridContext":
        return cls(
            client=context._client,  # type: ignore
            interaction_context=context,  # type: ignore
            invoke_target=context.invoke_target,
            command=context.command,
            args=context.args,
            kwargs=context.kwargs,
            author=context.author,
            channel=context.channel,
            guild_id=context.guild_id,
            deferred=context.deferred,
            responded=context.responded,
            app_permissions=context.app_permissions,
        )

    @classmethod
    def from_prefixed_context(cls, context: PrefixedContext) -> "HybridContext":
        # this is a "best guess" on what the permissions are
        # this may or may not be totally accurate
        if hasattr(context.channel, "permissions_for"):
            app_permissions = context.channel.permissions_for(context.guild.me)  # type: ignore
        elif context.channel.type in {10, 11, 12}:  # it's a thread
            app_permissions = context.channel.parent_channel.permissions_for(context.guild.me)  # type: ignore
        else:
            # this is what happens with interaction contexts in dms
            app_permissions = 0

        return cls(
            client=context._client,  # type: ignore
            prefixed_context=context,  # type: ignore
            invoke_target=context.invoke_target,
            command=context.command,
            args=context.args,
            kwargs=context.kwargs,  # this is usually empty
            author=context.author,
            channel=context.channel,
            guild_id=context.guild_id,
            message=context.message,
            app_permissions=app_permissions,
        )

    @property
    def inner_context(self) -> InteractionContext | PrefixedContext:
        """
        Returns the context powering the current hybrid context.

        This can be used for scope-specific actions, like sending modals in an interaction.
        """
        return self._interaction_context or self._prefixed_context  # type: ignore

    @property
    def ephemeral(self) -> bool:
        """Returns if responses to this interaction are ephemeral, if this is an interaction. Otherwise, returns False."""
        return self._interaction_context.ephemeral if self._interaction_context else False

    @property
    def expires_at(self) -> Optional[Timestamp]:
        """The timestamp the context is expected to expire at, or None if the context never expires."""
        if not self._interaction_context:
            return None

        if self.responded:
            return Timestamp.from_snowflake(self._interaction_context.interaction_id) + datetime.timedelta(minutes=15)
        return Timestamp.from_snowflake(self._interaction_context.interaction_id) + datetime.timedelta(seconds=3)

    @property
    def expired(self) -> bool:
        """Has the context expired yet?"""
        return Timestamp.utcnow() >= self.expires_at if self.expires_at else False

    @property
    def invoked_name(self) -> str:
        return (
            self.command.get_localised_name(self._interaction_context.locale)
            if self._interaction_context
            else self.invoke_target
        )

    async def defer(self, ephemeral: bool = False) -> None:
        """
        Either defers the response (if used in an interaction) or triggers a typing indicator for 10 seconds (if used for messages).

        Args:
            ephemeral: Should the response be ephemeral? Only applies to responses for interactions.

        """
        if self._interaction_context:
            await self._interaction_context.defer(ephemeral=ephemeral)
        else:
            await self.channel.trigger_typing()

        self.deferred = True

    async def reply(
        self,
        content: Optional[str] = None,
        embeds: Optional[Union[Iterable[Union["Embed", dict]], Union["Embed", dict]]] = None,
        embed: Optional[Union["Embed", dict]] = None,
        **kwargs,
    ) -> "Message":
        """
        Reply to this message, takes all the same attributes as `send`.

        For interactions, this functions the same as `send`.
        """
        kwargs = locals()
        kwargs.pop("self")
        extra_kwargs = kwargs.pop("kwargs")
        kwargs |= extra_kwargs

        if self._interaction_context:
            result = await self._interaction_context.send(**kwargs)
        else:
            kwargs.pop("ephemeral", None)
            result = await self._prefixed_context.reply(**kwargs)  # type: ignore

        self.responded = True
        return result

    async def send(
        self,
        content: Optional[str] = None,
        *,
        embeds: Optional[Union[Iterable[Union["Embed", dict]], Union["Embed", dict]]] = None,
        embed: Optional[Union["Embed", dict]] = None,
        components: Optional[
            Union[
                Iterable[Iterable[Union["BaseComponent", dict]]],
                Iterable[Union["BaseComponent", dict]],
                "BaseComponent",
                dict,
            ]
        ] = None,
        stickers: Optional[Union[Iterable[Union["Sticker", "Snowflake_Type"]], "Sticker", "Snowflake_Type"]] = None,
        allowed_mentions: Optional[Union["AllowedMentions", dict]] = None,
        reply_to: Optional[Union["MessageReference", "Message", dict, "Snowflake_Type"]] = None,
        file: Optional[Union["File", "IOBase", "Path", str]] = None,
        tts: bool = False,
        flags: Optional[Union[int, "MessageFlags"]] = None,
        ephemeral: bool = False,
        **kwargs,
    ) -> "Message":
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
            flags: Message flags to apply.
            ephemeral: Should this message be sent as ephemeral (hidden) - only works with interactions.

        Returns:
            New message object that was sent.

        """
        kwargs = locals()
        kwargs.pop("self")
        extra_kwargs = kwargs.pop("kwargs")
        kwargs |= extra_kwargs

        if self._interaction_context:
            result = await self._interaction_context.send(**kwargs)
        else:
            kwargs.pop("ephemeral", None)
            result = await self._prefixed_context.send(**kwargs)  # type: ignore

        self.responded = True
        return result


@runtime_checkable
class SendableContext(Protocol):
    """
    A protocol that supports any context that can send messages.

    Use it to type hint something that accepts both PrefixedContext and InteractionContext.
    """

    channel: "TYPE_MESSAGEABLE_CHANNEL"
    invoke_target: str

    author: Union["Member", "User"]
    guild_id: "Snowflake_Type"
    message: "Message"

    @property
    def bot(self) -> "Client":
        ...

    @property
    def guild(self) -> Optional["Guild"]:
        ...

    async def send(
        self,
        content: Optional[str] = None,
        *,
        embeds: Optional[Union[Iterable[Union["Embed", dict]], Union["Embed", dict]]] = None,
        embed: Optional[Union["Embed", dict]] = None,
        components: Optional[
            Union[
                Iterable[Iterable[Union["BaseComponent", dict]]],
                Iterable[Union["BaseComponent", dict]],
                "BaseComponent",
                dict,
            ]
        ] = None,
        stickers: Optional[Union[Iterable[Union["Sticker", "Snowflake_Type"]], "Sticker", "Snowflake_Type"]] = None,
        allowed_mentions: Optional[Union["AllowedMentions", dict]] = None,
        reply_to: Optional[Union["MessageReference", "Message", dict, "Snowflake_Type"]] = None,
        files: Optional[Union["UPLOADABLE_TYPE", Iterable["UPLOADABLE_TYPE"]]] = None,
        file: Optional["UPLOADABLE_TYPE"] = None,
        tts: bool = False,
        suppress_embeds: bool = False,
        flags: Optional[Union[int, "MessageFlags"]] = None,
        delete_after: Optional[float] = None,
        **kwargs: Any,
    ) -> "Message":
        ...
