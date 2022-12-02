from typing import TYPE_CHECKING, Any, Dict, List, Optional
from urllib.parse import quote

from ..models.channel import Channel
from ..models.guild import Guild
from ..models.role import Role
from .request import _Request
from .route import Route

if TYPE_CHECKING:
    from ...api.cache import Cache

__all__ = ("GuildRequest",)


class GuildRequest:
    _req: _Request
    cache: "Cache"

    def __init__(self) -> None:
        pass

    async def get_self_guilds(
        self, limit: Optional[int] = 200, before: Optional[int] = None, after: Optional[int] = None
    ) -> List[dict]:
        """
        Gets all guild objects associated with the current bot user.

        :param limit: Number of guilds to return. Defaults to 200.
        :param before: Consider only users before the given Guild ID snowflake.
        :param after: Consider only users after the given Guild ID snowflake.
        :return: A list of partial guild objects the current bot user is a part of.
        """

        params = {}
        if limit is not None:
            params["limit"] = limit
        if before:
            params["before"] = before
        if after:
            params["after"] = after

        request = await self._req.request(Route("GET", "/users/@me/guilds"), params=params)

        for guild in request:
            if guild.get("id"):
                self.cache[Guild].merge(Guild(**guild, _client=self))

        return request

    async def get_guild(self, guild_id: int, with_counts: bool = False) -> dict:
        """
        Requests an individual guild from the API.

        :param guild_id: The guild snowflake ID associated.
        :param with_counts: Whether the approximate member count should be included
        :return: The guild object associated, if any.
        """
        request = await self._req.request(
            Route("GET", f"/guilds/{guild_id}{f'?{with_counts=}' if with_counts else ''}")
        )
        self.cache[Guild].merge(Guild(**request, _client=self))

        return request

    async def get_guild_preview(self, guild_id: int) -> dict:
        """
        Get a guild's preview.

        :param guild_id: Guild ID snowflake.
        :return: Guild Preview object associated with the snowflake
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/preview"))

    async def modify_guild(
        self, guild_id: int, payload: dict, reason: Optional[str] = None
    ) -> dict:
        """
        Modifies a guild's attributes.

        :param guild_id: Guild ID snowflake.
        :param payload: The parameters to change.
        :param reason: Reason to send to the audit log, if given.
        :return: The modified guild object as a dictionary
        :rtype: dict
        """

        return await self._req.request(
            Route("PATCH", f"/guilds/{guild_id}"), json=payload, reason=reason
        )

    async def leave_guild(self, guild_id: int) -> None:
        """
        Leaves a guild.

        :param guild_id: The guild snowflake ID associated.
        :return: None
        """
        return await self._req.request(
            Route("DELETE", f"/users/@me/guilds/{guild_id}", guild_id=guild_id)
        )

    async def delete_guild(self, guild_id: int) -> None:
        """
        Deletes a guild.

        :param guild_id: Guild ID snowflake.
        """
        return await self._req.request(Route("DELETE", f"/guilds/{guild_id}"))

    async def get_guild_widget(self, guild_id: int) -> dict:
        """
        Returns the widget for the guild.

        :param guild_id: Guild ID snowflake.
        :return: Guild Widget contents as a dict: {"enabled":bool, "channel_id": str}
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/widget.json"))

    async def get_guild_widget_settings(self, guild_id: int) -> dict:
        """
        Get guild widget settings.

        :param guild_id: Guild ID snowflake.
        :return: Guild Widget contents as a dict: {"enabled":bool, "channel_id": str}
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}"))

    async def get_guild_widget_image(self, guild_id: int, style: Optional[str] = None) -> str:
        """
        Get an url representing a png image widget for the guild.

        .. note::
            See _<https://discord.com/developers/docs/resources/guild#get-guild-widget-image> for list of styles.

        :param guild_id: Guild ID snowflake.
        :param style: The style of widget required, if given.
        :return: A url pointing to this image
        """
        route = Route("GET", f"/guilds/{guild_id}/widget.png{f'?style={style}' if style else ''}")
        return route.path

    async def modify_guild_widget(self, guild_id: int, payload: dict) -> dict:
        """
        Modify a guild widget.

        :param guild_id: Guild ID snowflake.
        :param payload: Payload containing new widget attributes.
        :return: Updated widget attributes.
        """
        return await self._req.request(Route("PATCH", f"/guilds/{guild_id}/widget"), json=payload)

    async def get_guild_invites(self, guild_id: int) -> List[dict]:
        """
        Retrieves a list of invite objects with their own metadata.

        :param guild_id: Guild ID snowflake.
        :return: A list of invite objects
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/invites"))

    async def get_guild_welcome_screen(self, guild_id: int) -> dict:
        """
        Retrieves from the API a welcome screen associated with the guild.

        :param guild_id: Guild ID snowflake.
        :return: Welcome Screen object
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/welcome-screen"))

    async def modify_guild_welcome_screen(
        self, guild_id: int, enabled: bool, welcome_channels: List[int], description: str
    ) -> dict:
        """
        Modify the guild's welcome screen.

        :param guild_id: Guild ID snowflake.
        :param enabled: Whether the welcome screen is enabled or not.
        :param welcome_channels: The new channels (by their ID) linked in the welcome screen and their display options
        :param description: The new server description to show in the welcome screen
        :return: Updated Welcome screen object.
        """
        return await self._req.request(
            Route("PATCH", f"/guilds/{guild_id}/welcome-screen"),
            json={
                "enabled": enabled,
                "welcome_channels": welcome_channels,
                "description": description,
            },
        )

    async def get_vanity_code(self, guild_id: int) -> dict:
        return await self._req.request(
            Route("GET", "/guilds/{guild_id}/vanity-url", guild_id=guild_id)
        )

    async def modify_vanity_code(
        self, guild_id: int, code: str, reason: Optional[str] = None
    ) -> None:
        payload: Dict[str, Any] = {"code": code}
        return await self._req.request(
            Route("PATCH", "/guilds/{guild_id}/vanity-url", guild_id=guild_id),
            json=payload,
            reason=reason,
        )

    async def get_guild_integrations(self, guild_id: int) -> List[dict]:
        """
        Gets a list of integration objects associated with the Guild from the API.

        :param guild_id: Guild ID snowflake.
        :return: An array of integration objects
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/integrations"))

    async def delete_guild_integration(self, guild_id: int, integration_id: int) -> None:
        """
        Deletes an integration from the guild.

        :param guild_id: Guild ID snowflake.
        :param integration_id: Integration ID snowflake.
        """
        return await self._req.request(
            Route("DELETE", f"/guilds/{guild_id}/integrations/{integration_id}")
        )

    async def modify_current_user_voice_state(
        self,
        guild_id: int,
        channel_id: int,
        suppress: Optional[bool] = None,
        request_to_speak_timestamp: Optional[str] = None,
    ) -> None:
        """
        Update the current user voice state.

        :param guild_id: Guild ID snowflake.
        :param channel_id: Voice channel ID snowflake.
        :param suppress: Toggle the user's suppress state, if given.
        :param request_to_speak_timestamp: Sets the user's request to speak, if given.
        """
        return await self._req.request(
            Route("PATCH", f"/guilds/{guild_id}/voice-states/@me"),
            json={
                k: v
                for k, v in {
                    "channel_id": channel_id,
                    "suppress": suppress,
                    "request_to_speak_timestamp": request_to_speak_timestamp,
                }.items()
                if v is not None
            },
        )

    async def modify_user_voice_state(
        self, guild_id: int, user_id: int, channel_id: int, suppress: Optional[bool] = None
    ) -> None:
        """
        Modify the voice state of a user.

        :param guild_id: Guild ID snowflake.
        :param user_id: User ID snowflake.
        :param channel_id: Voice channel ID snowflake.
        :param suppress: Toggles the user's suppress state, if given.
        """
        return await self._req.request(
            Route("PATCH", f"/guilds/{guild_id}/voice-states/{user_id}"),
            json={
                k: v
                for k, v in {"channel_id": channel_id, "suppress": suppress}.items()
                if v is not None
            },
        )

    async def create_guild_from_guild_template(
        self, template_code: str, name: str, icon: Optional[str] = None
    ) -> dict:
        """
        Create a new guild based on a template.

        .. note::
            This endpoint can only be used by bots in less than 10 guilds.

        :param template_code: The code of the template to use.
        :param name: The name of the guild (2-100 characters)
        :param icon: Guild icon URI, if given.
        :return: The newly created guild object.
        """
        payload = {
            "name": name,
        }
        if icon:
            payload["icon"] = icon
        return await self._req.request(
            Route("POST", f"/guilds/templates/{template_code}"),
            json=payload,
        )

    async def get_guild_template(self, template_code: str) -> dict:
        """
        .. versionadded:: 4.4.0

        Returns a guild template.

        :param template_code: The code for the template to get
        :return: A guild template
        """
        return await self._req.request(Route("GET", f"/guilds/templates/{template_code}"))

    async def get_guild_templates(self, guild_id: int) -> List[dict]:
        """
        Returns an array of guild templates.

        :param guild_id: Guild ID snowflake.
        :return: An array of guild templates
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/templates"))

    async def create_guild_template(
        self, guild_id: int, name: str, description: Optional[str] = None
    ) -> dict:
        """
        Create a guild template for the guild.

        :param guild_id: Guild ID snowflake.
        :param name: The name of the template
        :param description: The description of the template, if given.
        :return: The created guild template
        """
        return await self._req.request(
            Route("POST", f"/guilds/{guild_id}/templates"),
            json={
                k: v for k, v in {"name": name, "description": description}.items() if v is not None
            },
        )

    async def sync_guild_template(self, guild_id: int, template_code: str) -> dict:
        """
        Sync the template to the guild's current state.

        :param guild_id: Guild ID snowflake.
        :param template_code: The code for the template to sync
        :return: The updated guild template.
        """
        return await self._req.request(
            Route("PUT", f"/guilds/{guild_id}/templates/{template_code}")
        )

    async def modify_guild_template(
        self,
        guild_id: int,
        template_code: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> dict:
        """
        Modify a guild template.

        :param guild_id: Guild ID snowflake.
        :param template_code: Template ID.
        :param name: The name of the template
        :param description: The description of the template
        :return: The updated guild template
        """
        return await self._req.request(
            Route("PATCH", f"/guilds/{guild_id}/templates/{template_code}"),
            json={
                k: v for k, v in {"name": name, "description": description}.items() if v is not None
            },
        )

    async def delete_guild_template(self, guild_id: int, template_code: str) -> dict:
        """
        Delete the guild template.

        :param guild_id: Guild ID snowflake.
        :param template_code: Template ID.
        :return: The deleted template object
        """
        # According to Polls, this returns the object. Why, I don't know.
        return await self._req.request(
            Route("DELETE", f"/guilds/{guild_id}/templates/{template_code}")
        )

    async def get_all_channels(self, guild_id: int) -> List[dict]:
        """
        Requests from the API to get all channels in the guild.

        :param guild_id: Guild Snowflake ID
        :return: A list of channels.
        """
        request = await self._req.request(
            Route("GET", "/guilds/{guild_id}/channels", guild_id=guild_id)
        )

        for channel in request:
            if channel.get("id"):
                self.cache[Channel].merge(Channel(**channel, _client=self))

        return request

    async def get_all_roles(self, guild_id: int) -> List[dict]:
        """
        Gets all roles from a Guild.

        :param guild_id: Guild ID snowflake
        :return: An array of Role objects as dictionaries.
        """
        request = await self._req.request(
            Route("GET", "/guilds/{guild_id}/roles", guild_id=guild_id)
        )

        for role in request:
            if role.get("id"):
                self.cache[Role].merge(Role(**role))

        return request

    async def create_guild_role(
        self, guild_id: int, payload: dict, reason: Optional[str] = None
    ) -> dict:
        """
        Create a new role for the guild.

        :param guild_id: Guild ID snowflake.
        :param payload: A dict containing metadata for the role.
        :param reason: The reason for this action, if given.
        :return: Role object
        """
        request = await self._req.request(
            Route("POST", f"/guilds/{guild_id}/roles"), json=payload, reason=reason
        )

        return request

    async def modify_guild_role_positions(
        self, guild_id: int, payload: List[dict], reason: Optional[str] = None
    ) -> List[dict]:
        """
        Modify the position of a role in the guild.

        :param guild_id: Guild ID snowflake.
        :param payload: A list of dicts containing the role IDs and new positions for all the roles to be moved.
        :param reason: The reason for this action, if given.
        :return: List of guild roles with updated hierarchy.
        """
        return await self._req.request(
            Route("PATCH", f"/guilds/{guild_id}/roles"),
            json=payload,
            reason=reason,
        )

    async def modify_guild_role(
        self, guild_id: int, role_id: int, payload: dict, reason: Optional[str] = None
    ) -> dict:
        """
        Modify a given role for the guild.

        :param guild_id: Guild ID snowflake.
        :param role_id: Role ID snowflake.
        :param payload: A dict containing updated metadata for the role.
        :param reason: The reason for this action, if given.
        :return: Updated role object.
        """
        return await self._req.request(
            Route("PATCH", f"/guilds/{guild_id}/roles/{role_id}"), json=payload, reason=reason
        )

    async def delete_guild_role(self, guild_id: int, role_id: int, reason: str = None) -> None:
        """
        Delete a guild role.

        :param guild_id: Guild ID snowflake.
        :param role_id: Role ID snowflake.
        :param reason: The reason for this action, if any.
        """
        return await self._req.request(
            Route("DELETE", f"/guilds/{guild_id}/roles/{role_id}"), reason=reason
        )

    async def create_guild_kick(
        self, guild_id: int, user_id: int, reason: Optional[str] = None
    ) -> None:
        """
        Kicks a person from the guild.

        :param guild_id: Guild ID snowflake
        :param user_id: User ID snowflake
        :param reason: Optional Reason argument.
        """
        r = Route(
            "DELETE", "/guilds/{guild_id}/members/{user_id}", guild_id=guild_id, user_id=user_id
        )
        if reason:  # apparently, its an aiohttp thing?
            r.path += f"?reason={quote(reason)}"

        await self._req.request(r)

    async def create_guild_ban(
        self,
        guild_id: int,
        user_id: int,
        delete_message_seconds: Optional[int] = 0,
        reason: Optional[str] = None,
    ) -> None:
        """
        Bans a person from the guild, and optionally deletes previous messages sent by them.

        :param guild_id: Guild ID snowflake
        :param user_id: User ID snowflake
        :param delete_message_seconds: Number of seconds to delete messages for, between 0 and 604800. Default to 0
        :param reason: Optional reason to ban.
        """

        return await self._req.request(
            Route("PUT", f"/guilds/{guild_id}/bans/{user_id}"),
            json={"delete_message_seconds": delete_message_seconds},
            reason=reason,
        )

    async def remove_guild_ban(
        self, guild_id: int, user_id: int, reason: Optional[str] = None
    ) -> None:
        """
        Unbans someone using the API.

        :param guild_id: Guild ID snowflake
        :param user_id: User ID snowflake
        :param reason: Optional reason to unban.
        """

        return await self._req.request(
            Route("DELETE", f"/guilds/{guild_id}/bans/{user_id}"),
            json={},
            reason=reason,
        )

    async def get_guild_bans(
        self,
        guild_id: int,
        limit: Optional[int] = 1000,
        before: Optional[int] = None,
        after: Optional[int] = None,
    ) -> List[dict]:
        """
        Gets a list of banned users.

        .. note::
            If both ``before`` and ``after`` are provided, only ``before`` is respected.

        :param guild_id: Guild ID snowflake.
        :param limit: Number of users to return. Defaults to 1000.
        :param before: Consider only users before the given User ID snowflake.
        :param after: Consider only users after the given User ID snowflake.
        :return: A list of banned users.
        """

        params = {}
        if limit is not None:
            params["limit"] = limit
        if before:
            params["before"] = before
        if after:
            params["after"] = after

        return await self._req.request(Route("GET", f"/guilds/{guild_id}/bans"), params=params)

    async def get_user_ban(self, guild_id: int, user_id: int) -> Optional[dict]:
        """
        Gets an object pertaining to the user, if it exists. Returns a 404 if it doesn't.

        :param guild_id: Guild ID snowflake
        :param user_id: User ID snowflake.
        :return: Ban object if it exists.
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/bans/{user_id}"))

    async def add_guild_member(
        self,
        guild_id: int,
        user_id: int,
        access_token: str,
        nick: Optional[str] = None,
        roles: Optional[List[Role]] = None,
        mute: bool = None,
        deaf: bool = None,
    ) -> dict:
        """
        A low level method of adding a user to a guild with pre-defined attributes.

        :param guild_id: Guild ID snowflake.
        :param user_id: User ID snowflake.
        :param access_token: User access token.
        :param nick: User's nickname on join.
        :param roles: An array of roles that the user is assigned.
        :param mute: Whether the user is mute in voice channels.
        :param deaf: Whether the user is deafened in voice channels.
        :return: Guild member object as dictionary
        """
        request = await self._req.request(
            Route("PUT", f"/guilds/{guild_id}/members/{user_id}"),
            json={
                k: v
                for k, v in {
                    "access_token": access_token,
                    "nick": nick,
                    "roles": roles,
                    "mute": mute,
                    "deaf": deaf,
                }.items()
                if v is not None
            },
        )

        return request

    async def remove_guild_member(
        self, guild_id: int, user_id: int, reason: Optional[str] = None
    ) -> None:
        """
        A low level method of removing a member from a guild. This is different from banning them.

        :param guild_id: Guild ID snowflake.
        :param user_id: User ID snowflake.
        :param reason: Reason to send to audit log, if any.
        """
        return await self._req.request(
            Route("DELETE", f"/guilds/{guild_id}/members/{user_id}"), reason=reason
        )

    async def begin_guild_prune(
        self,
        guild_id: int,
        days: int = 7,
        compute_prune_count: bool = True,
        include_roles: Optional[List[int]] = None,
    ) -> dict:
        """
        Begins a prune operation.

        :param guild_id: Guild ID snowflake
        :param days: Number of days to count, minimum 1, maximum 30. Defaults to 7.
        :param compute_prune_count: Whether the returned "pruned" dict contains the computed prune count or None.
        :param include_roles: Role IDs to include, if given.
        :return: A dict containing `{"pruned": int}` or `{"pruned": None}`
        """

        payload = {
            "days": days,
            "compute_prune_count": compute_prune_count,
        }
        if include_roles:
            payload["include_roles"] = ", ".join(str(x) for x in include_roles)

        return await self._req.request(Route("POST", f"/guilds/{guild_id}/prune"), json=payload)

    async def get_guild_prune_count(
        self, guild_id: int, days: int = 7, include_roles: Optional[List[int]] = None
    ) -> dict:
        """
        Retrieves a dict from an API that results in how many members would be pruned given the amount of days.

        :param guild_id: Guild ID snowflake.
        :param days: Number of days to count, minimum 1, maximum 30. Defaults to 7.
        :param include_roles: Role IDs to include, if given.
        :return: A dict denoting `{"pruned": int}`
        """
        payload = {"days": days}
        if include_roles:
            payload["include_roles"] = ", ".join(
                str(x) for x in include_roles
            )  # would still iterate

        return await self._req.request(Route("GET", f"/guilds/{guild_id}/prune"), params=payload)

    async def get_guild_auditlog(
        self,
        guild_id: int,
        user_id: Optional[int] = None,
        action_type: Optional[int] = None,
        before: Optional[int] = None,
        limit: int = 50,
    ) -> dict:
        """
        Returns an audit log object for the guild. Requires the 'VIEW_AUDIT_LOG' permission.
        :param guild_id: Guild ID snowflake.
        :param user_id: User ID snowflake. filter the log for actions made by a user.
        :param action_type: the type ID of audit log event.
        :param before: filter the log before a certain entry id.
        :param limit: how many entries are returned (default 50, minimum 1, maximum 100)
        """

        payload = {"limit": limit}
        if user_id:
            payload["user_id"] = user_id
        if action_type:
            payload["action_type"] = action_type
        if before:
            payload["before"] = before

        return await self._req.request(
            Route("GET", f"/guilds/{guild_id}/audit-logs"), params=payload
        )

    async def list_auto_moderation_rules(self, guild_id: int) -> List[dict]:
        """
        Returns a list of all AutoMod rules in a guild.
        :poram guild_id: Guild ID snowflake.
        :return: A list of dictionaries containing the automod rules.
        """

        return await self._req.request(Route("GET", f"/guilds/{guild_id}/auto-moderation/rules"))

    async def get_auto_moderation_rule(self, guild_id: int, rule_id: int) -> dict:
        """
        Get a single AutoMod rule in a guild.
        :param guild_id: Guild ID snowflake.
        :param rule_id: Rule ID snowflake.
        :return: A dictionary containing the automod rule.
        """

        return await self._req.request(
            Route("GET", f"/guilds/{guild_id}/auto-moderation/rules/{rule_id}")
        )

    async def create_auto_moderation_rule(
        self,
        guild_id: int,
        name: str,
        event_type: int,
        trigger_type: int,
        actions: List[dict],
        trigger_metadata: Optional[dict] = None,
        enabled: Optional[bool] = False,
        exempt_roles: Optional[List[str]] = None,
        exempt_channels: Optional[List[str]] = None,
        reason: Optional[str] = None,
    ) -> dict:
        """
        Create a new AutoMod rule in a guild.

        :param guild_id: Guild ID snowflake.
        :param name: The name of the new rule.
        :param event_type: The event type of the new rule.
        :param trigger_type: The trigger type of the new rule.
        :param trigger_metadata: The trigger metadata payload representation. This can be omitted based on the trigger type.
        :param actions: The actions that will execute when the rule is triggered.
        :param enabled: Whether the rule will be enabled upon creation. False by default.
        :param exempt_roles: The role IDs that are whitelisted by the rule, if given. The maximum is 20.
        :param exempt_channels: The channel IDs that are whitelisted by the rule, if given. The maximum is 20
        :param reason: Reason to send to audit log, if any.
        :return: A dictionary containing the new automod rule.
        """

        payload = {
            "name": name,
            "event_type": event_type,
            "trigger_type": trigger_type,
            "actions": actions,
            "enabled": enabled,
        }
        if trigger_metadata:
            payload["trigger_metadata"] = trigger_metadata
        if exempt_roles:
            payload["exempt_roles"] = exempt_roles
        if exempt_channels:
            payload["exempt_channels"] = exempt_channels

        return await self._req.request(
            Route("POST", f"/guilds/{guild_id}/auto-moderation/rules"), json=payload, reason=reason
        )

    async def modify_auto_moderation_rule(
        self,
        guild_id: int,
        rule_id: int,
        name: Optional[str] = None,
        event_type: Optional[int] = None,
        trigger_metadata: Optional[dict] = None,
        actions: Optional[List[dict]] = None,
        enabled: Optional[bool] = None,
        exempt_roles: Optional[List[str]] = None,
        exempt_channels: Optional[List[str]] = None,
        reason: Optional[str] = None,
    ) -> dict:
        """
        Modify an existing AutoMod rule in a guild.

        .. note ::
            All parameters besides guild and rule ID are optional.

        :param guild_id: Guild ID snowflake.
        :param rule_id: Rule ID snowflake.
        :param name: The new name of the rule.
        :param event_type: The new event type of the rule.
        :param trigger_metadata: The new trigger metadata payload representation. This can be omitted based on the trigger type.
        :param actions: The new actions that will execute when the rule is triggered.
        :param enabled: Whether the rule will be enabled upon creation.
        :param exempt_roles: The role IDs that are whitelisted by the rule, if given. The maximum is 20.
        :param exempt_channels: The channel IDs that are whitelisted by the rule, if given. The maximum is 20
        :param reason: Reason to send to audit log, if any.
        :return: A dictionary containing the updated automod rule.
        """
        payload = {}
        if name:
            payload["name"] = name
        if event_type:
            payload["event_type"] = event_type
        if trigger_metadata:
            payload["trigger_metadata"] = trigger_metadata
        if actions:
            payload["actions"] = actions
        if enabled:
            payload["enabled"] = enabled
        if exempt_roles:
            payload["exempt_roles"] = exempt_roles
        if exempt_channels:
            payload["exempt_channels"] = exempt_channels

        return await self._req.request(
            Route("PATCH", f"/guilds/{guild_id}/auto-moderation/rules/{rule_id}"),
            json=payload,
            reason=reason,
        )

    async def delete_auto_moderation_rule(
        self, guild_id: int, rule_id: int, reason: Optional[str] = None
    ) -> None:
        """
        Deletes an AutoMod rule.
        :param guild_id: Guild ID snowflake.
        :param rule_id: Rule ID snowflake.
        :param reason: Reason to send to audit log, if any.
        """

        return await self._req.request(
            Route("DELETE", f"/guilds/{guild_id}/auto-moderation/rules/{rule_id}"), reason=reason
        )
