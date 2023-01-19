import re
from typing import Any, Dict, Optional, Union

import aiohttp  # type: ignore

from interactions.client.const import get_logger

__all__ = ("OverriddenJson", "response_decode", "get_args", "get_first_word")

try:
    import orjson as json
except ImportError:
    get_logger().warning("orjson not installed, built-in json library will be used")
    import json as json


_quotes = {
    '"': '"',
    "‘": "’",
    "‚": "‛",
    "“": "”",
    "„": "‟",
    "⹂": "⹂",
    "「": "」",
    "『": "』",
    "〝": "〞",
    "﹁": "﹂",
    "﹃": "﹄",
    "＂": "＂",
    "｢": "｣",
    "«": "»",
    "‹": "›",
    "《": "》",
    "〈": "〉",
}
_pending_regex = r"(1.*2|[^\t\f\v ]+)"
_pending_regex = _pending_regex.replace("1", f"[{''.join(list(_quotes.keys()))}]")
_pending_regex = _pending_regex.replace("2", f"[{''.join(list(_quotes.values()))}]")

arg_parse = re.compile(_pending_regex)
white_space = re.compile(r"\s+")


class OverriddenJson:
    """Uses orjson if available, otherwise uses built-in json library."""

    @staticmethod
    def dumps(*args, **kwargs) -> str:
        data = json.dumps(*args, **kwargs)
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        return data

    @staticmethod
    def loads(*args, **kwargs) -> dict:
        return json.loads(*args, **kwargs)


async def response_decode(response: aiohttp.ClientResponse) -> Union[Dict[str, Any], str]:
    """
    Return the response text in its correct format, be it dict, or string.

    Args:
        response: the aiohttp response
    Returns:
        the response text field in its correct type

    """
    text = await response.text(encoding="utf-8")

    if response.headers.get("content-type") == "application/json":
        return OverriddenJson.loads(text)
    return text


def get_args(text: str) -> list:
    """
    Get arguments from an input text.

    Args:
        text: The text to process
    Returns:
        A list of words

    """
    return arg_parse.findall(text)


def get_first_word(text: str) -> Optional[str]:
    """
    Get a the first word in a string, regardless of whitespace type.

    Args:
        text: The text to process
    Returns:
         The requested word

    """
    return split[0] if (split := text.split(maxsplit=1)) else None
