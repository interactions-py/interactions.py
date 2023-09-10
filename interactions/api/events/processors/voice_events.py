import copy
from typing import TYPE_CHECKING

import interactions.api.events as events
from ._template import EventMixinTemplate, Processor

if TYPE_CHECKING:
    from interactions.api.events import RawGatewayEvent

__all__ = ("VoiceEvents",)


class VoiceEvents(EventMixinTemplate):
    @Processor.define()
    async def _on_raw_voice_state_update(self, event: "RawGatewayEvent") -> None:
        if str(event.data["user_id"]) == str(self.user.id):
            # User is the bot itself
            before = copy.copy(self.cache.get_bot_voice_state(event.data["guild_id"])) or None
            after = await self.cache.place_voice_state_data(event.data, update_cache=False)
            if vc := before:
                # noinspection PyProtectedMember
                await vc._voice_state_update(before, after, event.data)
        else:
            # User is not the bot
            before = copy.copy(self.cache.get_voice_state(event.data["user_id"])) or None
            after = await self.cache.place_voice_state_data(event.data)

        self.dispatch(events.VoiceStateUpdate(before, after))

        if before and after:
            if (before.mute != after.mute) or (before.self_mute != after.self_mute):
                self.dispatch(events.VoiceUserMute(after, after.member, after.channel, after.mute or after.self_mute))
            if (before.deaf != after.deaf) or (before.self_deaf != after.self_deaf):
                self.dispatch(events.VoiceUserDeafen(after, after.member, after.channel, after.deaf or after.self_deaf))
            if before.channel != after.channel:
                self.dispatch(events.VoiceUserMove(after, after.member, before.channel, after.channel))
        elif not before and after:
            self.dispatch(events.VoiceUserJoin(after, after.member, after.channel))
        elif before:
            self.dispatch(events.VoiceUserLeave(before, before.member, before.channel))

    @Processor.define()
    async def _on_raw_voice_server_update(self, event: "RawGatewayEvent") -> None:
        if vc := self.cache.get_bot_voice_state(event.data["guild_id"]):
            # noinspection PyProtectedMember
            await vc._voice_server_update(event.data)
