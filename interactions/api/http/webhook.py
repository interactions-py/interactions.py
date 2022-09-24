from typing import List, Optional

from aiohttp import MultipartWriter

from ...api.cache import Cache
from ...utils.missing import MISSING
from ..models.misc import File
from .request import _Request
from .route import Route

__all__ = ("WebhookRequest",)


class WebhookRequest:

    _req: _Request
    cache: Cache

    def __init__(self) -> None:
        pass

    async def create_webhook(self, channel_id: int, name: str, avatar: str = None) -> dict:
        """
        Create a new webhook.

        :param channel_id: Channel ID snowflake.
        :param name: Name of the webhook (1-80 characters)
        :param avatar: The image for the default webhook avatar, if given.

        :return: Webhook object
        """
        return await self._req.request(
            Route("POST", f"/channels/{channel_id}/webhooks"), json={"name": name, "avatar": avatar}
        )

    async def get_channel_webhooks(self, channel_id: int) -> List[dict]:
        """
        Return a list of channel webhook objects.

        :param channel_id: Channel ID snowflake.
        :return: List of webhook objects
        """
        return await self._req.request(Route("GET", f"/channels/{channel_id}/webhooks"))

    async def get_guild_webhooks(self, guild_id: int) -> List[dict]:
        """
        Return a list of guild webhook objects.

        :param guild_id: Guild ID snowflake
        :return: List of webhook objects
        """
        return await self._req.request(Route("GET", f"/guilds/{guild_id}/webhooks"))

    async def get_webhook(self, webhook_id: int, webhook_token: str = None) -> dict:
        """
        Return the new webhook object for the given id.

        :param webhook_id: Webhook ID snowflake.
        :param webhook_token: Webhook Token, if given.

        :return:Webhook object
        """
        endpoint = f"/webhooks/{webhook_id}{f'/{webhook_token}' if webhook_token else ''}"

        return await self._req.request(Route("GET", endpoint))

    async def modify_webhook(
        self,
        webhook_id: int,
        payload: dict,
        webhook_token: str = None,
    ) -> dict:
        """
        Modify a webhook.

        :param webhook_id: Webhook ID snowflake
        :param payload: The payload for the webhook
        :param webhook_token: The token for the webhook, if given.

        :return: Modified webhook object.
        """
        endpoint = f"/webhooks/{webhook_id}{f'/{webhook_token}' if webhook_token else ''}"

        return await self._req.request(
            Route("PATCH", endpoint),
            json=payload,
        )

    async def delete_webhook(self, webhook_id: int, webhook_token: str = None):
        """
        Delete a webhook.

        :param webhook_id: Webhook ID snowflake.
        :param webhook_token: The token for the webhook, if given.
        """

        endpoint = f"/webhooks/{webhook_id}{f'/{webhook_token}' if webhook_token else ''}"

        return await self._req.request(Route("DELETE", endpoint))

    async def execute_webhook(
        self,
        webhook_id: int,
        webhook_token: str,
        payload: dict,
        files: Optional[List[File]] = MISSING,
        wait: Optional[bool] = False,
        thread_id: Optional[int] = None,
    ) -> Optional[dict]:
        """
        Sends a message as a webhook.

        :param webhook_id: Webhook ID snowflake.
        :param webhook_token: The token for the webhook.
        :param payload: Payload consisting of the message.
        :param files: The files to upload to the message.
        :param wait: A bool that signifies waiting for server confirmation of a send before responding.
        :param thread_id: Optional, sends a message to the specified thread.
        :return: The message sent, if wait=True, else None.
        """

        data = None
        if files is not MISSING and len(files) > 0:

            data = MultipartWriter("form-data")
            part = data.append_json(payload)
            part.set_content_disposition("form-data", name="payload_json")
            payload = None

            for id, file in enumerate(files):
                part = data.append(
                    file._fp,
                )
                part.set_content_disposition(
                    "form-data", name=f"files[{str(id)}]", filename=file._filename
                )

        params = {"wait": "true" if wait else "false"}
        if thread_id:
            params["thread_id"] = thread_id

        return await self._req.request(
            Route("POST", f"/webhooks/{webhook_id}/{webhook_token}"),
            params=params,
            json=payload,
            data=data,
        )

    async def execute_slack_webhook(
        self, webhook_id: int, webhook_token: str, payload: dict
    ) -> None:
        """
        Sends a message to a Slack-compatible webhook.

        :param webhook_id: Webhook ID snowflake.
        :param webhook_token: The token for the webhook.
        :param payload: Payload consisting of the message.

        :return: ?

        .. note::
            Payload structure is different than Discord's. See `here <https://api.slack.com/messaging/webhooks>_` for more details.
        """

        return await self._req.request(
            Route("POST", f"/webhooks/{webhook_id}/{webhook_token}/slack"), json=payload
        )

    async def execute_github_webhook(
        self, webhook_id: int, webhook_token: str, payload: dict
    ) -> None:
        """
        Sends a message to a Github-compatible webhook.

        :param webhook_id: Webhook ID snowflake.
        :param webhook_token: The token for the webhook.
        :param payload: Payload consisting of the message.

        :return: ?

        .. note::
            Payload structure is different than Discord's. See `here <https://discord.com/developers/docs/resources/webhook#execute-githubcompatible-webhook>_` for more details.
        """

        return await self._req.request(
            Route("POST", f"/webhooks/{webhook_id}/{webhook_token}/github"), json=payload
        )

    async def get_webhook_message(
        self, webhook_id: int, webhook_token: str, message_id: int
    ) -> dict:
        """
        Retrieves a message sent from a Webhook.

        :param webhook_id: Webhook ID snowflake.
        :param webhook_token: Webhook token.
        :param message_id: Message ID snowflake,
        :return: A Message object.
        """

        return await self._req.request(
            Route("GET", f"/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}")
        )

    async def edit_webhook_message(
        self, webhook_id: int, webhook_token: str, message_id: int, data: dict
    ) -> dict:
        """
        Edits a message sent from a Webhook.

        :param webhook_id: Webhook ID snowflake.
        :param webhook_token: Webhook token.
        :param message_id: Message ID snowflake.
        :param data: A payload consisting of new message attributes.
        :return: An updated message object.
        """

        return await self._req.request(
            Route("PATCH", f"/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}"),
            json=data,
        )

    async def delete_webhook_message(
        self, webhook_id: int, webhook_token: str, message_id: int
    ) -> None:
        """
        Deletes a message object.

        :param webhook_id: Webhook ID snowflake.
        :param webhook_token: Webhook token.
        :param message_id: Message ID snowflake.
        """

        return await self._req.request(
            Route("DELETE", f"/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}")
        )

    async def delete_original_webhook_message(self, webhook_id: int, webhook_token: str) -> None:
        """
        Deletes the original message object sent.

        :param webhook_id: Webhook ID snowflake.
        :param webhook_token: Webhook token.
        """

        return await self._req.request(
            Route("DELETE", f"/webhooks/{webhook_id}/{webhook_token}/messages/@original")
        )
