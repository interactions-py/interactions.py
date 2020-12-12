import aiohttp
from .error import RequestFailure


class SlashCommandRequest:
    def __init__(self):
        pass

    async def post(self, _resp, _id, token):
        """
        Sends command response POST request to Discord API.

        :param _resp: Command response.
        :type _resp: dict
        :param _id: Command message id.
        :param token: Command message token.
        :return: True if succeeded.
        :raises: :class:`error.RequestFailure` - Requesting to API has failed.
        """
        req_url = f"https://discord.com/api/v8/interactions/{_id}/{token}/callback"
        async with aiohttp.ClientSession() as session:
            async with session.post(req_url, json=_resp) as resp:
                if not 200 <= resp.status < 300:
                    raise RequestFailure(resp.status, await resp.text())
                return True
