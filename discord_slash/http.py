import json
import typing
import aiohttp
import discord
from discord.http import Route


class CustomRoute(Route):
    """discord.py's Route but changed ``BASE`` to use at slash command."""
    BASE = "https://discord.com/api/v8"


class SlashCommandRequest:
    def __init__(self, logger, _discord):
        self.logger = logger
        self._discord: typing.Union[discord.Client, discord.AutoShardedClient] = _discord

    def post(self, _resp, wait: bool, bot_id, interaction_id, token, initial=False, files: typing.List[discord.File] = None):
        """
        Sends command response POST request to Discord API.

        :param _resp: Command response.
        :type _resp: dict
        :param wait: Whether the server should wait before sending a response.
        :type wait: bool
        :param bot_id: Bot ID.
        :param interaction_id: Interaction ID.
        :param token: Command message token.
        :param initial: Whether this request is initial. Default ``False``
        :param files: Files to send. Default ``None``
        :type files: List[discord.File]
        :return: Coroutine
        """
        if files:
            return self.post_with_files(_resp, wait, files, bot_id, token)
        req_url = f"/interactions/{interaction_id}/{token}/callback" if initial else f"/webhooks/{bot_id}/{token}?wait={'true' if wait else 'false'}"
        route = CustomRoute("POST", req_url)
        return self._discord.http.request(route, json=_resp)

    def post_with_files(self, _resp, wait: bool, files: typing.List[discord.File], bot_id, token):
        req_url = f"/webhooks/{bot_id}/{token}?wait={'true' if wait else 'false'}"
        route = CustomRoute("POST", req_url)
        form = aiohttp.FormData()
        form.add_field("payload_json", json.dumps(_resp))
        for x in range(len(files)):
            name = f"file{x if len(files) > 1 else ''}"
            sel = files[x]
            form.add_field(name, sel.fp, filename=sel.filename, content_type="application/octet-stream")
        return self._discord.http.request(route, data=form, files=files)

    def edit(self, _resp, bot_id, token, message_id="@original"):
        """
        Sends edit command response POST request to Discord API.

        :param _resp: Edited response.
        :type _resp: dict
        :param bot_id: Bot ID.
        :param token: Command message token.
        :param message_id: Message ID to edit. Default initial message.
        :return: Coroutine
        """
        req_url = f"/webhooks/{bot_id}/{token}/messages/{message_id}"
        route = CustomRoute("PATCH", req_url)
        return self._discord.http.request(route, json=_resp)

    def delete(self, bot_id, token, message_id="@original"):
        """
        Sends delete command response POST request to Discord API.

        :param bot_id: Bot ID.
        :param token: Command message token.
        :param message_id: Message ID to delete. Default initial message.
        :return: Coroutine
        """
        req_url = f"/webhooks/{bot_id}/{token}/messages/{message_id}"
        route = CustomRoute("DELETE", req_url)
        return self._discord.http.request(route)
