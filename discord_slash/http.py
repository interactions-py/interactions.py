import aiohttp


class SlashCommandRequest:
    def __init__(self):
        pass

    async def post(self, _resp, _id, token):
        req_url = f"https://discord.com/api/v8/interactions/{_id}/{token}/callback"
        async with aiohttp.ClientSession() as session:
            async with session.post(req_url, json=_resp) as resp:
                if not 200 <= resp.status < 300:
                    raise Exception(f"Request failed with resp: {resp.status} | {await resp.text()}")
                return True
