from typing import TYPE_CHECKING

import attrs

from interactions.models.discord.base import DiscordObject, ClientObject
from interactions.models.discord.enums import InteractionPermissionTypes
from interactions.models.discord.snowflake import to_snowflake

if TYPE_CHECKING:
    from interactions import BaseContext
    from interactions import Snowflake_Type, Guild

__all__ = ("ApplicationCommandPermission",)


@attrs.define(eq=False, order=False, hash=False, kw_only=True)
class ApplicationCommandPermission(DiscordObject):
    id: "Snowflake_Type" = attrs.field(repr=False, converter=to_snowflake)
    """ID of the role user or channel"""
    type: InteractionPermissionTypes = attrs.field(repr=False, converter=InteractionPermissionTypes)
    """Type of permission (role user or channel)"""
    permission: bool = attrs.field(repr=False, default=False)
    """Whether the command is enabled for this permission"""


@attrs.define(eq=False, order=False, hash=False, kw_only=True)
class CommandPermissions(ClientObject):
    command_id: "Snowflake_Type" = attrs.field(
        repr=False,
    )
    _guild: "Guild" = attrs.field(
        repr=False,
    )

    permissions: dict["Snowflake_Type", ApplicationCommandPermission] = attrs.field(
        repr=False, factory=dict, init=False
    )

    def is_enabled(self, *object_id) -> bool:
        """
        Check if a command is enabled for given scope(s). Takes into account the permissions for the bot itself

        Args:
            *object_id: The object(s) ID to check for.

        Returns:
            Whether the command is enabled for the given scope(s).
        """
        bot_perms = self._guild.command_permissions.get(self._client.app.id)

        for obj_id in object_id:
            obj_id = to_snowflake(obj_id)
            if permission := self.permissions.get(obj_id):
                if not permission.permission:
                    return False

            if bot_perms:
                if permission := bot_perms.permissions.get(obj_id):
                    if not permission.permission:
                        return False
        return True

    def is_enabled_in_context(self, context: "BaseContext") -> bool:
        """
        Check if a command is enabled for the given context.

        Args:
            context: The context to check for.

        Returns:
            Whether the command is enabled for the given context.
        """
        everyone_role = context.guild.id
        all_channels = context.guild.id - 1  # why tf discord
        return self.is_enabled(
            context.channel.id,
            *context.member.roles,
            context.author.id,
            everyone_role,
            all_channels,
        )

    def update_permissions(self, *permissions: ApplicationCommandPermission) -> None:
        """
        Update the permissions for the command.

        Args:
            permissions: The permission to set.
        """
        self.permissions = {perm.id: perm for perm in permissions}
