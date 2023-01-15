from typing import TYPE_CHECKING

from interactions.models.discord.app_perms import ApplicationCommandPermission, CommandPermissions
from interactions.models.discord.snowflake import to_snowflake
from ._template import EventMixinTemplate, Processor
from ... import events

if TYPE_CHECKING:
    from interactions.api.events import RawGatewayEvent

__all__ = ("IntegrationEvents",)


class IntegrationEvents(EventMixinTemplate):
    @Processor.define()
    async def _raw_application_command_permissions_update(self, event: "RawGatewayEvent") -> None:
        perms = [ApplicationCommandPermission.from_dict(perm, self) for perm in event.data["permissions"]]
        guild_id = to_snowflake(event.data["guild_id"])
        command_id = to_snowflake(event.data["id"])

        if guild := self.get_guild(guild_id):
            if guild.permissions:
                if command_id not in guild.command_permissions:
                    guild.command_permissions[command_id] = CommandPermissions(
                        client=self, command_id=command_id, guild=guild
                    )

                command_permissions = guild.command_permissions[command_id]
                command_permissions.update_permissions(*perms)

        self.dispatch(events.ApplicationCommandPermissionsUpdate(guild, perms))
