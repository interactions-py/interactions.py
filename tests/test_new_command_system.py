from pprint import pprint  # noqa todo remove

import pytest  # noqa

import interactions


def test_basic_command(fake_client):
    @fake_client.command()
    async def command(ctx: interactions.CommandContext):
        """Hello!"""

    assert command.full_data == {
        "default_member_permissions": "2147483648",
        "description": "Hello!",
        "description_localizations": {},
        "dm_permission": True,
        "name": "command",
        "name_localizations": {},
        "options": [],
        "type": 1,
    }


def test_basic_command_with_required_option_with_read_from_kwargs(fake_client):
    @fake_client.command()
    @interactions.option("hi")
    async def command(ctx, option: str):
        """Hello!"""

    assert command.full_data == {
        "default_member_permissions": "2147483648",
        "description": "Hello!",
        "description_localizations": {},
        "dm_permission": True,
        "name": "command",
        "name_localizations": {},
        "options": [
            {
                "description": "hi",
                "name": "option",
                "required": True,
                "type": interactions.OptionType.STRING,
            }
        ],
        "type": 1,
    }


# todo not required, no read from kwargs x2, connector, localizations on everything, choices, default perms, dm perms

# todo for helpers maybe replace _request?
