import aiohttp
import asyncio
from .error import RequestFailure


class SlashCommandRequest:
    def __init__(self, logger):
        self.logger = logger

    async def post(self, _resp, bot_id, interaction_id, token, initial=False) -> None:
        """
        Sends command response POST request to Discord API.

        :param _resp: Command response.
        :type _resp: dict
        :param bot_id: Bot ID.
        :param interaction_id: Interaction ID.
        :param token: Command message token.
        :param initial: Whether this request is initial. Default ``False``
        :return: ``None``, since Discord API doesn't return anything.
        :raises: :class:`.error.RequestFailure` - Requesting to API has failed.
        """
        req_url = f"https://discord.com/api/v8/interactions/{interaction_id}/{token}/callback" \
            if initial \
            else f"https://discord.com/api/v8/webhooks/{bot_id}/{token}"
        async with aiohttp.ClientSession() as session:
            async with session.post(req_url, json=_resp) as resp:
                if resp.status == 429:
                    _json = await resp.json()
                    self.logger.warning(f"We are being rate limited, retrying after {_json['retry_after']} seconds.")
                    await asyncio.sleep(_json["retry_after"])
                    return await self.post(_resp, bot_id, interaction_id, token, initial)
                if not 200 <= resp.status < 300:
                    raise RequestFailure(resp.status, await resp.text())
                return None

    async def edit(self, _resp, bot_id, token, message_id="@original"):
        """
        Sends edit command response POST request to Discord API.

        :param _resp: Edited response.
        :type _resp: dict
        :param bot_id: Bot ID.
        :param token: Command message token.
        :param message_id: Message ID to edit. Default initial message.
        :return: True if succeeded.
        :raises: :class:`.error.RequestFailure` - Requesting to API has failed.
        """
        req_url = f"https://discord.com/api/v8/webhooks/{bot_id}/{token}/messages/{message_id}"
        async with aiohttp.ClientSession() as session:
            async with session.patch(req_url, json=_resp) as resp:
                if resp.status == 429:
                    _json = await resp.json()
                    self.logger.warning(f"We are being rate limited, retrying after {_json['retry_after']} seconds.")
                    await asyncio.sleep(_json["retry_after"])
                    return await self.edit(_resp, bot_id, token, message_id)
                if not 200 <= resp.status < 300:
                    raise RequestFailure(resp.status, await resp.text())
                return True

    async def delete(self, bot_id, token, message_id="@original"):
        """
        Sends delete command response POST request to Discord API.

        :param bot_id: Bot ID.
        :param token: Command message token.
        :param message_id: Message ID to delete. Default initial message.
        :return: True if succeeded.
        :raises: :class:`.error.RequestFailure` - Requesting to API has failed.
        """
        req_url = f"https://discord.com/api/v8/webhooks/{bot_id}/{token}/messages/{message_id}"
        async with aiohttp.ClientSession() as session:
            async with session.delete(req_url) as resp:
                if resp.status == 429:
                    _json = await resp.json()
                    self.logger.warning(f"We are being rate limited, retrying after {_json['retry_after']} seconds.")
                    await asyncio.sleep(_json["retry_after"])
                    return await self.delete(bot_id, token, message_id)
                if not 200 <= resp.status < 300:
                    raise RequestFailure(resp.status, await resp.text())
                return True
