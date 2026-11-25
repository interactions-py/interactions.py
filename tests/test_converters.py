import pytest

from interactions.client.errors import BadArgument
from interactions.models.internal.converters import PartialEmojiConverter
from tests.utils import generate_dummy_context

__all__ = ()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("argument", "name", "animated"),
    [
        ("<:thonk:123456789012345678>", "thonk", False),
        ("<a:party_blob:123456789012345678>", "party_blob", True),
    ],
)
async def test_partial_emoji_converter(argument: str, name: str, animated: bool) -> None:
    context = generate_dummy_context()
    emoji = await PartialEmojiConverter().convert(context, argument)

    assert emoji.id == 123456789012345678
    assert emoji.name == name
    assert emoji.animated is animated


@pytest.mark.asyncio
async def test_partial_emoji_converter_invalid() -> None:
    context = generate_dummy_context()
    with pytest.raises(BadArgument):
        await PartialEmojiConverter().convert(context, "not an emoji")
