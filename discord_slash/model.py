import typing
import discord
from discord.ext import commands
from . import http


class SlashContext:
    def __init__(self,
                 _http: http.SlashCommandRequest,
                 _json: dict,
                 _discord: commands.Bot):
        self.__token = _json["token"]
        self.name = _json["data"]["name"]
        self.__id = _json["id"]
        self.id = _json["data"]["id"]
        self._http = _http
        self.guild: discord.Guild = _discord.get_guild(int(_json["guild_id"]))
        self.author: discord.Member = self.guild.get_member(int(_json["member"]["user"]["id"]))

    async def send(self,
                   send_type: int = 4,
                   text: str = "",
                   embeds: typing.List[discord.Embed] = None,
                   tts: bool = False):
        base = {
            "type": send_type,
            "data": {
                "tts": tts,
                "content": text,
                "embeds": [x.to_dict() for x in embeds] if embeds else [],
                "allowed_mentions": []
            }
        }
        await self._http.post(base, self.__id, self.__token)


"""
{
    "type": 2,
    "token": "A_UNIQUE_TOKEN",
    "member": { 
        "user": {
            "id": 53908232506183680,
            "username": "Mason",
            "avatar": "a_d5efa99b3eeaa7dd43acca82f5692432",
            "discriminator": "1337",
            "public_flags": 131141
        },
        "roles": [539082325061836999],
        "premium_since": null,
        "permissions": "2147483647",
        "pending": false,
        "nick": null,
        "mute": false,
        "joined_at": "2017-03-13T19:19:14.040000+00:00",
        "is_pending": false,
        "deaf": false 
    },
    "id": "786008729715212338",
    "guild_id": "290926798626357999",
    "data": { 
        "options": [{
            "name": "cardname",
            "value": "The Gitrog Monster"
        }],
        "name": "cardsearch",
        "id": "771825006014889984" 
    },
    "channel_id": "645027906669510667" 
}
"""
