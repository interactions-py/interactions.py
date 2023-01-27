import io
import pprint
from collections import Counter
from typing import Optional

from interactions import Extension
from interactions.client.client import Client
from interactions.client.const import GLOBAL_SCOPE
from interactions.client.errors import HTTPException
from interactions.models import (
    slash_command,
    InteractionContext,
    File,
    Message,
    slash_option,
    OptionTypes,
    application_commands_to_dict,
)
from interactions.models.internal import checks
from .utils import debug_embed

__all__ = ("DebugAppCMD",)

app_cmds_def = {
    "group_name": "app_cmds",
    "group_description": "Debug for application commands",
}


class DebugAppCMD(Extension):
    def __init__(self, bot: Client) -> None:
        self.add_ext_check(checks.is_owner())

    @slash_command(
        "debug",
        sub_cmd_name="internal_info",
        sub_cmd_description="Get Information about registered app commands",
        **app_cmds_def,
    )
    async def app_cmd(self, ctx: InteractionContext) -> None:
        await ctx.defer()
        e = debug_embed("Application-Commands Cache")

        cmds = 0
        for v in self.bot.interactions.values():
            cmds += len(v.keys())

        e.add_field("Local application cmds (incld. Subcommands)", str(cmds))
        e.add_field("Component callbacks", str(len(self.bot._component_callbacks)))
        e.add_field("Prefixed commands", str(len(self.bot.prefixed_commands)))
        e.add_field(
            "Tracked Scopes",
            str(len(Counter(scope for scope in self.bot._interaction_scopes.values()).keys())),
        )

        await ctx.send(embeds=[e])

    @app_cmd.subcommand(
        "lookup",
        sub_cmd_description="Search for a specified command and get its json representation",
        **app_cmds_def,
    )
    @slash_option(
        "cmd_id",
        "The ID of the command you want to lookup",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    @slash_option(
        "scope",
        "The scope ID of the command, if you want to search for the cmd on remote",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    @slash_option(
        "remote",
        "Should we search locally or remote for this command (default local)",
        opt_type=OptionTypes.BOOLEAN,
        required=False,
    )
    async def cmd_lookup(
        self, ctx: InteractionContext, cmd_id: str, scope: str, remote: bool = False
    ) -> Optional[Message]:
        await ctx.defer()
        try:
            cmd_id = int(cmd_id.strip())
            scope = int(scope.strip())

            # search internal registers for command

            async def send(cmd_json: dict) -> None:
                await ctx.send(
                    file=File(
                        io.BytesIO(pprint.pformat(cmd_json, 2).encode("utf-8")),
                        f"{cmd_json.get('name')}.json",
                    )
                )

            if not remote:
                data = application_commands_to_dict(self.bot.interactions, self.bot)[scope]
                cmd_obj = self.bot.get_application_cmd_by_id(cmd_id)
                for cmd in data:
                    if cmd["name"] == cmd_obj.name:
                        return await send(cmd)

            else:
                data = await self.bot.http.get_application_commands(self.bot.app.id, scope)
                try:
                    perm_scope = scope
                    if scope == GLOBAL_SCOPE:
                        perm_scope = ctx.guild_id
                    perms = await self.bot.http.get_application_command_permissions(self.bot.app.id, perm_scope, cmd_id)
                except HTTPException:
                    perms = None
                for cmd in data:
                    if int(cmd["id"]) == cmd_id:
                        if perms:
                            cmd["permissions"] = perms.get("permissions")
                        return await send(cmd)
        except Exception:  # noqa: S110
            pass
        return await ctx.send(f"Unable to locate any commands in {scope} with ID {cmd_id}!")

    @app_cmd.subcommand(
        "list_scope",
        sub_cmd_description="List all synced commands in a specified scope",
        **app_cmds_def,
    )
    @slash_option(
        "scope",
        "The scope ID of the command, if it is not registered in the bot (0 for global)",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    async def list_scope(self, ctx: InteractionContext, scope: str) -> Message:
        await ctx.defer()
        try:
            cmds = await self.bot.http.get_application_commands(self.bot.app.id, int(scope.strip()))
            if cmds:
                e = debug_embed("Application Command Information")

                e.description = f"**Listing Commands Registered in {scope}**\n\n" + "\n".join(
                    [f"`{c['id']}` : `{c['name']}`" for c in cmds]
                )
                return await ctx.send(embeds=e)
            else:
                return await ctx.send(f"No commands found in `{scope.strip()}`")
        except Exception:
            return await ctx.send(f"No commands found in `{scope.strip()}`")


def setup(bot: Client) -> None:
    DebugAppCMD(bot)
