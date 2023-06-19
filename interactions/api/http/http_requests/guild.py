from typing import TYPE_CHECKING, Any, List, Mapping, cast

import discord_typings

from interactions.client.utils.serializer import dict_filter_none
from interactions.models.internal.protocols import CanRequest

from ..route import PAYLOAD_TYPE, Route

__all__ = ("GuildRequests",)


if TYPE_CHECKING:
    from interactions.models.discord.enums import AuditLogEventType
    from interactions.models.discord.snowflake import Snowflake_Type


class GuildRequests(CanRequest):
    async def get_guilds(
        self,
        limit: int = 200,
        before: "Snowflake_Type | None" = None,
        after: "Snowflake_Type | None" = None,
    ) -> list[discord_typings.GuildData]:
        """
        Get a list of partial guild objects the current user is a member of req. `guilds` scope.

        Args:
            limit: max number of guilds to return (1-200)
            before: get guilds before this guild ID
            after: get guilds after this guild ID

        Returns:
            List of guild objects

        """
        params: PAYLOAD_TYPE = {
            "limit": limit,
            "before": int(before) if before else None,
            "after": int(after) if after else None,
        }
        params = dict_filter_none(params)

        result = await self.request(Route("GET", "/users/@me/guilds", params=params))
        return cast(list[discord_typings.GuildData], result)

    async def get_guild(self, guild_id: "Snowflake_Type", with_counts: bool = True) -> discord_typings.GuildData:
        """
        Get the guild object for the given ID.

        Args:
            guild_id: the id of the guild
            with_counts: when `true`, will return approximate member and presence counts for the guild
        Returns:
            a guild object

        """
        params = {"with_counts": int(with_counts)}
        result = await self.request(Route("GET", "/guilds/{guild_id}", guild_id=guild_id), params=params)
        return cast(discord_typings.GuildData, result)

    async def get_guild_preview(self, guild_id: "Snowflake_Type") -> discord_typings.GuildPreviewData:
        """
        Get a guild's preview.

        Args:
            guild_id: the guilds ID

        Returns:
            guild preview object

        """
        result = await self.request(Route("GET", "/guilds/{guild_id}/preview", guild_id=guild_id))
        return cast(discord_typings.GuildPreviewData, result)

    async def get_channels(self, guild_id: "Snowflake_Type") -> list[discord_typings.ChannelData]:
        """
        Get a guilds channels.

        Args:
            guild_id: the id of the guild

        Returns:
            List of channels

        """
        result = await self.request(Route("GET", "/guilds/{guild_id}/channels", guild_id=guild_id))
        return cast(list[discord_typings.ChannelData], result)

    async def get_roles(self, guild_id: "Snowflake_Type") -> list[discord_typings.RoleData]:
        """
        Get a guild's roles.

        Args:
            guild_id: The ID of the guild

        Returns:
            List of roles

        """
        result = await self.request(Route("GET", "/guilds/{guild_id}/roles", guild_id=guild_id))
        return cast(list[discord_typings.RoleData], result)

    async def modify_guild(
        self, guild_id: "Snowflake_Type", reason: str | None = None, **kwargs: Mapping[str, Any]
    ) -> None:
        """
        Modify a guild's attributes.

        Args:
            guild_id: The ID of the guild we want to modify
            reason: The reason for this change
            **kwargs: The params to change

        """
        expected = (
            "name",
            "region",
            "verification_level",
            "default_message_notifications",
            "explicit_content_filter",
            "afk_channel_id",
            "afk_timeout",
            "icon",
            "owner_id",
            "splash",
            "discovery_splash",
            "banner",
            "system_channel_id",
            "system_channel_flags",
            "rules_channel_id",
            "public_updates_channel_id",
            "preferred_locale",
            "features",
            "description",
        )
        payload = kwargs.copy()
        for key, value in kwargs.items():
            if key not in expected or value is None:
                del payload[key]

        # only do the request if there is something to modify
        if payload:
            await self.request(Route("PATCH", "/guilds/{guild_id}", guild_id=guild_id), payload=payload, reason=reason)

    async def delete_guild(self, guild_id: "Snowflake_Type") -> None:
        """
        Delete the guild.

        Args:
            guild_id: The ID of the guild that we want to delete

        """
        await self.request(Route("DELETE", "/guilds/{guild_id}", guild_id=guild_id))

    async def add_guild_member(
        self,
        guild_id: "Snowflake_Type",
        user_id: "Snowflake_Type",
        access_token: str,
        nick: str | None = None,
        roles: list["Snowflake_Type"] | None = None,
        mute: bool = False,
        deaf: bool = False,
    ) -> discord_typings.GuildMemberData:
        """
        Add a user to the guild. All parameters to this endpoint except for `access_token`, `guild_id` and `user_id` are optional.

        Args:
            guild_id: The ID of the guild
            user_id: The ID of the user to add
            access_token: The access token of the user
            nick: value to set users nickname to
            roles: array of role ids the member is assigned
            mute: whether the user is muted in voice channels
            deaf: whether the user is deafened in voice channels
        Returns:
            Guild Member Object

        """
        payload = {
            "access_token": access_token,
            "nick": nick,
            "roles": [int(role) for role in roles] if roles else None,
            "mute": mute,
            "deaf": deaf,
        }
        payload = dict_filter_none(payload)

        result = await self.request(
            Route("PUT", "/guilds/{guild_id}/members/{user_id}", guild_id=guild_id, user_id=user_id), payload=payload
        )
        return cast(discord_typings.GuildMemberData, result)

    async def remove_guild_member(
        self, guild_id: "Snowflake_Type", user_id: "Snowflake_Type", reason: str | None = None
    ) -> None:
        """
        Remove a member from a guild.

        Args:
            guild_id: The ID of the guild
            user_id: The ID of the user to remove
            reason: The reason for this action

        """
        await self.request(
            Route("DELETE", "/guilds/{guild_id}/members/{user_id}", guild_id=guild_id, user_id=user_id), reason=reason
        )

    async def get_guild_bans(
        self,
        guild_id: "Snowflake_Type",
        before: "Snowflake_Type | None" = None,
        after: "Snowflake_Type | None" = None,
        limit: int = 1000,
    ) -> list[discord_typings.BanData]:
        """
        Return a list of ban objects for the users banned from this guild.

        Args:
            guild_id: The ID of the guild to query
            before: snowflake to get entries before
            after: snowflake to get entries after
            limit: max number of entries to get

        Returns:
            List of ban objects

        """
        params: PAYLOAD_TYPE = {
            "limit": limit,
            "before": int(before) if before else None,
            "after": int(after) if after else None,
        }
        params = dict_filter_none(params)

        result = await self.request(Route("GET", "/guilds/{guild_id}/bans", guild_id=guild_id), params=params)
        return cast(list[discord_typings.BanData], result)

    async def get_guild_ban(self, guild_id: "Snowflake_Type", user_id: "Snowflake_Type") -> discord_typings.BanData:
        """
        Returns a ban object for the given user or a 404 not found if the ban cannot be found.

        Args:
            guild_id: The ID of the guild to query
            user_id: The ID of the user to query

        Returns:
            Ban object if exists

        Raises:
            NotFound: if no ban exists

        """
        result = await self.request(
            Route("GET", "/guilds/{guild_id}/bans/{user_id}", guild_id=guild_id, user_id=user_id)
        )
        return cast(discord_typings.BanData, result)

    async def create_guild_ban(
        self,
        guild_id: "Snowflake_Type",
        user_id: "Snowflake_Type",
        delete_message_seconds: int = 0,
        reason: str | None = None,
    ) -> None:
        """
        Create a guild ban, and optionally delete previous messages sent by the banned user.

        Args:
            guild_id: The ID of the guild to create the ban in
            user_id: The ID of the user to ban
            delete_message_seconds: number of seconds to delete messages for (0-604800)
            reason: The reason for this action

        """
        payload = {"delete_message_seconds": delete_message_seconds}
        await self.request(
            Route("PUT", "/guilds/{guild_id}/bans/{user_id}", guild_id=guild_id, user_id=user_id),
            payload=payload,
            reason=reason,
        )

    async def remove_guild_ban(
        self, guild_id: "Snowflake_Type", user_id: "Snowflake_Type", reason: str | None = None
    ) -> None:
        """
        Remove a guild ban.

        Args:
            guild_id: The ID of the guild to remove the ban in
            user_id: The ID of the user to unban
            reason: The reason for this action

        """
        await self.request(
            Route("DELETE", "/guilds/{guild_id}/bans/{user_id}", guild_id=guild_id, user_id=user_id), reason=reason
        )

    async def get_guild_prune_count(
        self,
        guild_id: "Snowflake_Type",
        days: int = 7,
        include_roles: list["Snowflake_Type"] | None = None,
    ) -> dict:
        """
        Returns an object with one 'pruned' key indicating the number of members that would be removed in a prune operation.

        Args:
            guild_id: The ID of the guild to query
            days: number of days to count prune for (1-30)
            include_roles: role(s) to include

        Returns:
            {"pruned": int}

        """
        params: PAYLOAD_TYPE = {
            "days": days,
            "include_roles": ", ".join(str(int(role)) for role in include_roles) if include_roles else None,
        }
        params = dict_filter_none(params)

        result = await self.request(Route("GET", "/guilds/{guild_id}/prune", guild_id=guild_id), params=params)
        return cast(dict, result)  # todo revisit, create TypedDict for pruned

    async def begin_guild_prune(
        self,
        guild_id: "Snowflake_Type",
        days: int = 7,
        include_roles: list["Snowflake_Type"] | None = None,
        compute_prune_count: bool = True,
        reason: str | None = None,
    ) -> dict:
        """
        Begin a prune operation.

        Args:
            guild_id: The ID of the guild to query
            days: number of days to count prune for (1-30)
            include_roles: role(s) to include
            compute_prune_count: whether 'pruned' is returned, discouraged for large guilds
            reason: The reason for this action

        Returns:
            {"pruned": Optional[int]}

        """
        payload: PAYLOAD_TYPE = {
            "days": days,
            "compute_prune_count": compute_prune_count,
            "include_roles": ", ".join(str(int(role)) for role in include_roles) if include_roles else None,
        }
        payload = dict_filter_none(payload)

        result = await self.request(
            Route("POST", "/guilds/{guild_id}/prune", guild_id=guild_id), payload=payload, reason=reason
        )
        return cast(dict, result)  # todo revisit, create TypedDict for pruned

    async def get_guild_invites(self, guild_id: "Snowflake_Type") -> list[discord_typings.InviteData]:
        """
        Returns a list of invite objects (with invite metadata) for the guild.

        Args:
            guild_id: The ID of the guild to query

        Returns:
            List of invite objects

        """
        result = await self.request(Route("GET", "/guilds/{guild_id}/invites", guild_id=guild_id))
        return cast(list[discord_typings.InviteData], result)

    async def create_guild_role(
        self, guild_id: "Snowflake_Type", payload: dict, reason: str | None = None
    ) -> discord_typings.RoleData:
        """
        Create a new role for the guild.

        Args:
            guild_id: The ID of the guild
            payload: A dict representing the role to add
            reason: The reason for this action

        Returns:
            Role object

        """
        result = await self.request(
            Route("POST", "/guilds/{guild_id}/roles", guild_id=guild_id), payload=payload, reason=reason
        )
        return cast(discord_typings.RoleData, result)

    async def modify_guild_role_positions(
        self,
        guild_id: "Snowflake_Type",
        position_changes: List[dict["Snowflake_Type", int]],
        reason: str | None = None,
    ) -> list[discord_typings.RoleData]:
        """
        Modify the position of a role in the guild.

        Args:
            guild_id: The ID of the guild
            position_changes: A list of dicts representing the roles to move and their new positions
            reason: The reason for this action

        Returns:
            List of guild roles

        """
        payload: PAYLOAD_TYPE = [
            {"id": int(role["id"]), "position": int(role["position"])} for role in position_changes
        ]
        result = await self.request(
            Route("PATCH", "/guilds/{guild_id}/roles", guild_id=guild_id), payload=payload, reason=reason
        )
        return cast(list[discord_typings.RoleData], result)

    async def modify_guild_role(
        self,
        guild_id: "Snowflake_Type",
        role_id: "Snowflake_Type",
        payload: dict,
        reason: str | None = None,
    ) -> discord_typings.RoleData:
        """
        Modify an existing role for the guild.

        Args:
            guild_id: The ID of the guild
            role_id: The ID of the role to move
            payload: A dict representing the role to add
            reason: The reason for this action

        Returns:
            Role object

        """
        result = await self.request(
            Route("PATCH", "/guilds/{guild_id}/roles/{role_id}", guild_id=guild_id, role_id=role_id),
            payload=payload,
            reason=reason,
        )
        return cast(discord_typings.RoleData, result)

    async def delete_guild_role(
        self, guild_id: "Snowflake_Type", role_id: "Snowflake_Type", reason: str | None = None
    ) -> None:
        """
        Delete a guild role.

        Args:
            role_id: The ID of the role to delete
            reason: The reason for this action
            guild_id: The ID of the guild

        """
        await self.request(
            Route("DELETE", "/guilds/{guild_id}/roles/{role_id}", guild_id=guild_id, role_id=role_id), reason=reason
        )

    async def get_audit_log(
        self,
        guild_id: "Snowflake_Type",
        user_id: "Snowflake_Type | None" = None,
        action_type: "AuditLogEventType | None" = None,
        before: "Snowflake_Type | None" = None,
        after: "Snowflake_Type | None" = None,
        limit: int = 100,
    ) -> discord_typings.AuditLogData:
        """
        Get the audit log for a guild.

        Args:
            guild_id: The ID of the guild to query
            user_id: filter by user ID
            action_type: filter by action type
            before: snowflake to get entries before
            after: snowflake to get entries after
            limit: max number of entries to get

        Returns:
            audit log object for the guild

        """
        params: PAYLOAD_TYPE = {
            "limit": limit,
            "before": int(before) if before else None,
            "after": int(after) if after else None,
            "user_id": int(user_id) if user_id else None,
            "action_type": int(action_type) if action_type else None,
        }
        params = dict_filter_none(params)

        result = await self.request(Route("GET", "/guilds/{guild_id}/audit-logs", guild_id=guild_id), params=params)
        return cast(discord_typings.AuditLogData, result)

    async def get_guild_voice_regions(self, guild_id: "Snowflake_Type") -> list[discord_typings.VoiceRegionData]:
        """
        Returns a list of voice region objects for the guild. Unlike the similar /voice route, this returns VIP servers when the guild is VIP- enabled.

        Args:
            guild_id: The ID of the guild to query

        Returns:
            List of voice region objects

        """
        result = await self.request(Route("GET", "/guilds/{guild_id}/regions", guild_id=guild_id))
        return cast(list[discord_typings.VoiceRegionData], result)

    async def get_guild_integrations(self, guild_id: "Snowflake_Type") -> list[discord_typings.IntegrationData]:
        """
        Returns a list of integration objects for the guild.

        Args:
            guild_id: The ID of the guild to query

        Returns:
            list of integration objects

        """
        result = await self.request(Route("GET", "/guilds/{guild_id}/integrations", guild_id=guild_id))
        return cast(list[discord_typings.IntegrationData], result)

    async def delete_guild_integration(
        self,
        guild_id: "Snowflake_Type",
        integration_id: "Snowflake_Type",
        reason: str | None = None,
    ) -> None:
        """
        Delete an integration from the guild.

        Args:
            guild_id: The ID of the guild
            integration_id: The ID of the integration to remove
            reason: The reason for this action

        """
        await self.request(
            Route(
                "DELETE",
                "/guilds/{guild_id}/integrations/{integration_id}",
                guild_id=guild_id,
                integration_id=integration_id,
            ),
            reason=reason,
        )

    async def get_guild_widget_settings(self, guild_id: "Snowflake_Type") -> discord_typings.GuildWidgetSettingsData:
        """
        Get guild widget settings.

        Args:
            guild_id: The ID of the guild to query

        Returns:
            guild widget object

        """
        result = await self.request(Route("GET", "/guilds/{guild_id}/widget", guild_id=guild_id))
        return cast(discord_typings.GuildWidgetSettingsData, result)

    async def get_guild_widget(self, guild_id: "Snowflake_Type") -> discord_typings.GuildWidgetData:
        """
        Returns the widget for the guild.

        Args:
            guild_id: The ID of the guild to query

        Returns:
            Guild widget

        """
        result = await self.request(Route("GET", "/guilds/{guild_id}/widget.json", guild_id=guild_id))
        return cast(discord_typings.GuildWidgetData, result)

    async def get_guild_widget_image(self, guild_id: "Snowflake_Type", style: str | None = None) -> str:
        """
        Get a url representing a png image widget for the guild.

        For styles see: https://discord.com/developers/docs/resources/guild#get-guild-widget-image

        Args:
            guild_id: The guild to query
            style: The style of widget required.

        Returns:
            A url pointing to this image

        """
        route = Route(
            "GET", "/guilds/{guild_id}/widget.png{style}", guild_id=guild_id, style="?style={style}" if style else ""
        )
        return route.url

    async def get_guild_welcome_screen(self, guild_id: "Snowflake_Type") -> discord_typings.WelcomeScreenData:
        """
        Get the welcome screen for this guild.

        Args:
            guild_id: The ID of the guild to query
        Returns:
            Welcome screen object

        """
        result = await self.request(Route("GET", "/guilds/{guild_id}/welcome-screen", guild_id=guild_id))
        return cast(discord_typings.WelcomeScreenData, result)

    async def get_guild_vanity_url(self, guild_id: "Snowflake_Type") -> dict:
        """
        Get a partial invite object for the guilds vanity invite url.

        Args:
            guild_id: The ID of the guild to query

        Returns:
            Returns a partial invite object. Code is None if a vanity url for the guild is not set.

        """
        result = await self.request(Route("GET", "/guilds/{guild_id}/vanity-url", guild_id=guild_id))
        return cast(dict, result)  # todo create typing?

    async def get_guild_channels(
        self, guild_id: "Snowflake_Type"
    ) -> list[discord_typings.ChannelData]:  # todo narrow down channel types
        """
        Gets a list of guild channel objects.

        Args:
            guild_id: The ID of the guild

        Returns:
            A list of channels in this guild. Does not include threads.
        """
        result = await self.request(Route("GET", "/guilds/{guild_id}/channels", guild_id=guild_id))
        return cast(list[discord_typings.ChannelData], result)

    async def modify_guild_widget(
        self,
        guild_id: "Snowflake_Type",
        enabled: bool | None = None,
        channel_id: "Snowflake_Type | None" = None,
    ) -> discord_typings.GuildWidgetData:
        """
        Modify a guild widget.

        Args:
            guild_id: The ID of the guild to modify.
            enabled: Should the guild widget be enabled
            channel_id: The widget's channel ID

        Returns:
            Updated guild widget.

        """
        payload: PAYLOAD_TYPE = {
            "enabled": enabled,
            "channel_id": int(channel_id) if channel_id else None,
        }
        payload = dict_filter_none(payload)

        result = await self.request(Route("PATCH", "/guilds/{guild_id}/widget", guild_id=guild_id), payload=payload)
        return cast(discord_typings.GuildWidgetData, result)

    async def modify_guild_welcome_screen(
        self,
        guild_id: "Snowflake_Type",
        enabled: bool,
        welcome_channels: list["Snowflake_Type"],
        description: str,
    ) -> discord_typings.WelcomeScreenData:
        """
        Modify the guild's welcome screen.

        Args:
            guild_id: The ID of the guild.
            enabled: Whether the welcome screen is enabled
            welcome_channels: Channels linked in the welcome screen and their display options
            description: The server description to show in the welcome screen

        Returns:
            Updated welcome screen object

        """
        payload: PAYLOAD_TYPE = {
            "enabled": enabled,
            "welcome_channels": [int(channel) for channel in welcome_channels],
            "description": description,
        }
        result = await self.request(
            Route("PATCH", "/guilds/{guild_id}/welcome-screen", guild_id=guild_id), payload=payload
        )
        return cast(discord_typings.WelcomeScreenData, result)

    async def modify_current_user_voice_state(
        self,
        guild_id: "Snowflake_Type",
        channel_id: "Snowflake_Type",
        suppress: bool | None = None,
        request_to_speak_timestamp: str | None = None,
    ) -> None:
        """
        Update the current user voice state.

        Args:
            guild_id: The ID of the guild to update.
            channel_id: The id of the channel the user is currently in
            suppress: Toggle the user's suppress state.
            request_to_speak_timestamp: Sets the user's request to speak

        """
        payload: PAYLOAD_TYPE = {
            "suppress": suppress,
            "request_to_speak_timestamp": request_to_speak_timestamp,
            "channel_id": int(channel_id) if channel_id else None,
        }
        payload = dict_filter_none(payload)

        await self.request(Route("PATCH", "/guilds/{guild_id}/voice-states/@me", guild_id=guild_id), payload=payload)

    async def modify_user_voice_state(
        self,
        guild_id: "Snowflake_Type",
        user_id: "Snowflake_Type",
        channel_id: "Snowflake_Type",
        suppress: bool | None = None,
    ) -> None:
        """
        Modify the voice state of a user.

        Args:
            guild_id: The ID of the guild.
            user_id: The ID of the user to modify.
            channel_id: The ID of the channel the user is currently in.
            suppress: Toggles the user's suppress state.

        """
        payload: PAYLOAD_TYPE = {
            "suppress": suppress,
            "channel_id": int(channel_id) if channel_id else None,
        }
        payload = dict_filter_none(payload)

        await self.request(
            Route("PATCH", "/guilds/{guild_id}/voice-states/{user_id}", guild_id=guild_id, user_id=user_id),
            payload=payload,
        )

    async def create_guild(
        self,
        name: str,
        icon: str | None = None,
        verification_level: int | None = None,
        default_message_notifications: int | None = None,
        explicit_content_filter: int | None = None,
        roles: list[dict] | None = None,
        channels: list[dict] | None = None,
        afk_channel_id: "Snowflake_Type | None" = None,
        afk_timeout: int | None = None,
        system_channel_id: "Snowflake_Type | None" = None,
        system_channel_flags: int | None = None,
    ) -> discord_typings.GuildData:
        payload = {
            "name": name,
            "icon": icon,
            "verification_level": verification_level,
            "default_message_notifications": default_message_notifications,
            "explicit_content_filter": explicit_content_filter,
            "roles": roles,
            "channels": channels,
            "afk_channel_id": int(afk_channel_id) if afk_channel_id else None,
            "afk_timeout": afk_timeout,
            "system_channel_id": int(system_channel_id) if system_channel_id else None,
            "system_channel_flags": system_channel_flags,
        }
        payload = dict_filter_none(payload)

        result = await self.request(Route("POST", "/guilds"), payload=payload)
        return cast(discord_typings.GuildData, result)

    async def create_guild_from_guild_template(
        self, template_code: str, name: str, icon: str
    ) -> discord_typings.GuildData:
        """
        Creates a new guild based on a template.

        !!! note
            This endpoint can only be used by bots in less than 10 guilds.

        Args:
            template_code: The code of the template to use.
            name: The name of the guild (2-100 characters)
            icon: Data URI scheme

        Returns:
            The newly created guild object

        """
        payload = {"name": name, "icon": icon}

        result = await self.request(
            Route("POST", "/guilds/templates/{template_code}", template_code=template_code), payload=payload
        )
        return cast(discord_typings.GuildData, result)

    async def get_guild_templates(self, guild_id: "Snowflake_Type") -> list[discord_typings.GuildTemplateData]:
        """
        Returns an array of guild templates.

        Args:
            guild_id: The ID of the guild to query.

        Returns:
            An array of guild templates

        """
        result = await self.request(Route("GET", "/guilds/{guild_id}/templates", guild_id=guild_id))
        return cast(list[discord_typings.GuildTemplateData], result)

    async def create_guild_template(
        self, guild_id: "Snowflake_Type", name: str, description: str | None = None
    ) -> discord_typings.GuildTemplateData:
        """
        Create a guild template for the guild.

        Args:
            guild_id: The ID of the guild to create a template for.
            name: The name of the template
            description: The description of the template

        Returns:
            The created guild template

        """
        payload = {"name": name, "description": description}
        payload = dict_filter_none(payload)

        result = await self.request(Route("POST", "/guilds/{guild_id}/templates", guild_id=guild_id), payload=payload)
        return cast(discord_typings.GuildTemplateData, result)

    async def sync_guild_template(
        self, guild_id: "Snowflake_Type", template_code: str
    ) -> discord_typings.GuildTemplateData:
        """
        Sync the template to the guild's current state.

        Args:
            guild_id: The ID of the guild
            template_code: The code for the template to sync

        Returns:
            The updated guild template

        """
        result = await self.request(
            Route("PUT", "/guilds/{guild_id}/templates/{template_code}", guild_id=guild_id, template_code=template_code)
        )
        return cast(discord_typings.GuildTemplateData, result)

    async def modify_guild_template(
        self,
        guild_id: "Snowflake_Type",
        template_code: str,
        name: str | None = None,
        description: str | None = None,
    ) -> discord_typings.GuildTemplateData:
        """
        Modifies the template's metadata.

        Args:
            guild_id: The ID of the guild
            template_code: The template code
            name: The name of the template
            description: The description of the template

        Returns:
            The updated guild template

        """
        payload: PAYLOAD_TYPE = {"name": name, "description": description}
        payload = dict_filter_none(payload)

        result = await self.request(
            Route(
                "PATCH", "/guilds/{guild_id}/templates/{template_code}", guild_id=guild_id, template_code=template_code
            ),
            payload=payload,
        )
        return cast(discord_typings.GuildTemplateData, result)

    async def delete_guild_template(
        self, guild_id: "Snowflake_Type", template_code: str
    ) -> discord_typings.GuildTemplateData:
        """
        Delete the guild template.

        Args:
            guild_id: The ID of the guild
            template_code: The ID of the template

        Returns:
            The deleted template object

        """
        # why on earth does this return the deleted template object?
        result = await self.request(
            Route(
                "DELETE", "/guilds/{guild_id}/templates/{template_code}", guild_id=guild_id, template_code=template_code
            )
        )
        return cast(discord_typings.GuildTemplateData, result)

    async def get_auto_moderation_rules(
        self, guild_id: "Snowflake_Type"
    ) -> list[discord_typings.AutoModerationRuleData]:
        """
        Get this guilds auto moderation rules.

        Args:
            guild_id: The ID of the guild to get

        Returns:
            A list of auto moderation rules
        """
        result = await self.request(Route("GET", "/guilds/{guild_id}/auto-moderation/rules", guild_id=guild_id))
        return cast(list[dict], result)

    async def get_auto_moderation_rule(
        self, guild_id: "Snowflake_Type", rule_id: "Snowflake_Type"
    ) -> discord_typings.AutoModerationRuleData:
        """
        Get a specific auto moderation rule.

        Args:
            guild_id: The ID of the guild
            rule_id: The ID of the rule to get

        Returns:
            The auto moderation rule
        """
        result = await self.request(
            Route("GET", "/guilds/{guild_id}/auto-moderation/rules/{rule_id}", guild_id=guild_id, rule_id=rule_id)
        )
        return cast(dict, result)

    async def create_auto_moderation_rule(
        self, guild_id: "Snowflake_Type", payload: discord_typings.AutoModerationRuleData
    ) -> discord_typings.AutoModerationRuleData:
        """
        Create an auto moderation rule.

        Args:
            guild_id: The ID of the guild to create this rule within
            payload: A dict representing the auto moderation rule

        Returns:
            The created auto moderation rule
        """
        result = await self.request(
            Route("POST", "/guilds/{guild_id}/auto-moderation/rules", guild_id=guild_id), payload=payload
        )
        return cast(dict, result)

    async def modify_auto_moderation_rule(
        self,
        guild_id: "Snowflake_Type",
        rule_id: "Snowflake_Type",
        name: str | None = None,
        trigger_type: dict | None = None,
        trigger_metadata: dict | None = None,
        actions: list[dict] | None = None,
        exempt_channels: list["Snowflake_Type"] | None = None,
        exempt_roles: list["Snowflake_Type"] | None = None,
        event_type: dict | None = None,
        enabled: bool | None = None,
        reason: str | None = None,
    ) -> dict:
        """
        Modify an existing auto moderation rule.

        Args:
            guild_id: The ID of the guild the rule belongs to
            rule_id: The ID of the rule to modify
            name: The name of the rule
            trigger_type: The type trigger for this rule
            trigger_metadata: Metadata for the trigger
            actions: A list of actions to take upon triggering
            exempt_roles: Roles that ignore this rule
            exempt_channels: Channels that ignore this role
            enabled: Is this rule enabled?
            event_type: The type of event that triggers this rule
            reason: The reason for this change

        Returns:
            The updated rule object
        """
        payload = {
            "name": name,
            "trigger_type": trigger_type,
            "trigger_metadata": trigger_metadata,
            "actions": actions,
            "exempt_roles": [int(role) for role in exempt_roles] if exempt_roles else None,
            "exempt_channels": [int(channel) for channel in exempt_channels] if exempt_channels else None,
            "event_type": event_type,
            "enabled": enabled,
        }
        payload = dict_filter_none(payload)

        result = await self.request(
            Route("PATCH", "/guilds/{guild_id}/auto-moderation/rules/{rule_id}", guild_id=guild_id, rule_id=rule_id),
            payload=payload,
            reason=reason,
        )
        return cast(dict, result)

    async def delete_auto_moderation_rule(
        self, guild_id: "Snowflake_Type", rule_id: "Snowflake_Type", reason: str | None = None
    ) -> dict:
        """
        Delete an auto moderation rule.

        Args:
            guild_id: The ID of the guild to delete this rule from
            rule_id: The ID of the role to delete
            reason: The reason for deleting this rule
        """
        result = await self.request(
            Route("DELETE", "/guilds/{guild_id}/auto-moderation/rules/{rule_id}", guild_id=guild_id, rule_id=rule_id),
            reason=reason,
        )
        return cast(dict, result)
