from pprint import pprint  # noqa todo remove

import pytest  # noqa

import interactions


def test_basic_command(fake_client):
    @fake_client.command()
    async def command(ctx: interactions.CommandContext):
        """Hello!"""

    assert command.full_data == dict(
        default_member_permissions="2147483648",
        description="Hello!",
        description_localizations={},
        dm_permission=True,
        name="command",
        name_localizations={},
        options=[],
        type=1,
    )


def test_basic_command_with_required_option_with_read_from_kwargs(fake_client):
    @fake_client.command()
    @interactions.option("hi")
    async def command(ctx, option: str):
        """Hello!"""

    assert command.full_data == dict(
        default_member_permissions="2147483648",
        description="Hello!",
        description_localizations={},
        dm_permission=True,
        name="command",
        name_localizations={},
        options=[
            {
                "description": "hi",
                "name": "option",
                "required": True,
                "type": interactions.OptionType.STRING,
            }
        ],
        type=1,
    )


def test_basic_command_with_not_required_option_with_read_from_kwargs(fake_client):
    @fake_client.command()
    @interactions.option("hi")
    async def command(ctx, option: str = ""):
        """Hello!"""

    assert command.full_data == dict(
        default_member_permissions="2147483648",
        description="Hello!",
        description_localizations={},
        dm_permission=True,
        name="command",
        name_localizations={},
        options=[
            {
                "description": "hi",
                "name": "option",
                "required": False,
                "type": interactions.OptionType.STRING,
            }
        ],
        type=1,
    )


def test_basic_command_with_required_option_with_read_from_option_decorator(fake_client):
    @fake_client.command()
    @interactions.option("hi", type=interactions.OptionType.USER, required=True)
    async def command(ctx, option: str = None):
        """Hello!"""

    assert command.full_data == dict(
        default_member_permissions="2147483648",
        description="Hello!",
        description_localizations={},
        dm_permission=True,
        name="command",
        name_localizations={},
        options=[
            {
                "description": "hi",
                "name": "option",
                "required": True,
                "type": interactions.OptionType.USER,
            }
        ],
        type=1,
    )


def test_basic_command_with_not_required_option_with_read_from_option_decorator(fake_client):
    @fake_client.command()
    @interactions.option("hi", type=interactions.OptionType.USER, required=False)
    async def command(ctx, option: str):
        """Hello!"""

    assert command.full_data == dict(
        default_member_permissions="2147483648",
        description="Hello!",
        description_localizations={},
        dm_permission=True,
        name="command",
        name_localizations={},
        options=[
            {
                "description": "hi",
                "name": "option",
                "required": False,
                "type": interactions.OptionType.USER,
            }
        ],
        type=1,
    )


def test_basic_command_with_connector_option_with_read_from_kwargs(fake_client):
    @fake_client.command()
    @interactions.option("hi", name="hi")
    async def command(ctx, d: interactions.Member):
        """Hello!"""

    assert command.full_data == dict(
        default_member_permissions="2147483648",
        description="Hello!",
        description_localizations={},
        dm_permission=True,
        name="command",
        name_localizations={},
        options=[
            {
                "description": "hi",
                "name": "hi",
                "required": True,
                "type": interactions.OptionType.USER,
            }
        ],
        type=1,
    ) and command.converters == {"hi": "d"}


def test_basic_command_with_connector_option(fake_client):
    @fake_client.command()
    @interactions.option(
        "hi", name="hi", type=interactions.OptionType.USER, required=True, connector="d"
    )
    async def command(ctx, d: str = None):
        """Hello!"""

    assert command.full_data == dict(
        default_member_permissions="2147483648",
        description="Hello!",
        description_localizations={},
        dm_permission=True,
        name="command",
        name_localizations={},
        options=[
            {
                "connector": "d",
                "description": "hi",
                "name": "hi",
                "required": True,
                "type": interactions.OptionType.USER,
            }
        ],
        type=1,
    ) and command.converters == {"hi": "d"}


def test_basic_command_with_converter_option(fake_client):
    @fake_client.command()
    @interactions.option(
        "hi", name="hi", type=interactions.OptionType.USER, required=True, converter="d"
    )
    async def command(ctx, d: str = None):
        """Hello!"""

    assert command.full_data == dict(
        default_member_permissions="2147483648",
        description="Hello!",
        description_localizations={},
        dm_permission=True,
        name="command",
        name_localizations={},
        options=[
            {
                "description": "hi",
                "name": "hi",
                "required": True,
                "type": interactions.OptionType.USER,
            }
        ],
        type=1,
    ) and command.converters == {"hi": "d"}


def test_basic_command_with_perms(fake_client):
    @fake_client.command(dm_permission=False, default_member_permissions=8)
    async def command(ctx):
        """Hello!"""

    assert command.full_data == dict(
        default_member_permissions="8",
        description="Hello!",
        description_localizations={},
        dm_permission=False,
        name="command",
        name_localizations={},
        options=[],
        type=1,
    )


def test_basic_command_with_option_choices(fake_client):
    @fake_client.command()
    @interactions.option(
        "hi",
        choices=[
            interactions.Choice(name="hi", value="hi"),
            interactions.Choice(name="bye", value="bye"),
        ],
    )
    async def command(ctx, option: str = ""):
        """Hello!"""

    assert command.full_data == dict(
        default_member_permissions="2147483648",
        description="Hello!",
        description_localizations={},
        dm_permission=True,
        name="command",
        name_localizations={},
        options=[
            {
                "choices": [{"name": "hi", "value": "hi"}, {"name": "bye", "value": "bye"}],
                "description": "hi",
                "name": "option",
                "required": False,
                "type": interactions.OptionType.STRING,
            }
        ],
        type=1,
    )


def test_basic_invalid_command_failure(fake_client):
    fake_client._commands = []

    @fake_client.command(name="HI")
    async def command(ctx):
        """Hello!"""

    with pytest.raises(interactions.LibraryException):
        fake_client._Client__resolve_commands()


def test_basic_command_with_invalid_option_failure(fake_client):
    fake_client._commands = []

    @fake_client.command()
    @interactions.option("hi", name="HI")
    async def command(ctx, hi: str):
        """Hello!"""

    with pytest.raises(interactions.LibraryException):
        fake_client._Client__resolve_commands()


# todo localizations on everything, also make subcmds with all tests as above

# todo for helpers maybe replace _request?
