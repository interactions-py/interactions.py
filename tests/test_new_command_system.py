import pytest

import interactions

# done


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


def test_basic_command_with_localizations(fake_client):
    @fake_client.command(
        name_localizations={interactions.Locale.GERMAN: "befehl"},
        description_localizations={interactions.Locale.GERMAN: "Hallo!"},
    )
    async def command(ctx: interactions.CommandContext):
        """Hello!"""

    assert command.full_data == dict(
        default_member_permissions="2147483648",
        description="Hello!",
        description_localizations={"de": "Hallo!"},
        dm_permission=True,
        name="command",
        name_localizations={"de": "befehl"},
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


def test_basic_command_with_required_option_with_read_from_kwargs_and_localisations(fake_client):
    @fake_client.command(
        name_localizations={interactions.Locale.GERMAN: "befehl"},
        description_localizations={interactions.Locale.GERMAN: "Hallo!"},
    )
    @interactions.option(
        "hi",
        name_localizations={interactions.Locale.GERMAN: "option"},
        description_localizations={interactions.Locale.GERMAN: "Hi"},
    )
    async def command(ctx, option: str):
        """Hello!"""

    assert command.full_data == dict(
        default_member_permissions="2147483648",
        description="Hello!",
        description_localizations={"de": "Hallo!"},
        dm_permission=True,
        name="command",
        name_localizations={"de": "befehl"},
        options=[
            {
                "description": "hi",
                "description_localizations": {"de": "Hi"},
                "name": "option",
                "name_localizations": {"de": "option"},
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


def test_basic_command_with_multiple_options(fake_client):
    @fake_client.command()
    @interactions.option("hi")
    @interactions.option("hi")
    @interactions.option("hi")
    async def command(ctx, name: str, number: int, person: interactions.Member):
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
                "name": "name",
                "required": True,
                "type": interactions.OptionType.STRING,
            },
            {
                "description": "hi",
                "name": "number",
                "required": True,
                "type": interactions.OptionType.INTEGER,
            },
            {
                "description": "hi",
                "name": "person",
                "required": True,
                "type": interactions.OptionType.USER,
            },
        ],
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


def test_sub_command(fake_client):
    @fake_client.command()
    async def base(*args, **kwargs):
        pass

    @base.subcommand()
    async def command(ctx):
        """OwO!"""

    assert base.full_data == dict(
        default_member_permissions="2147483648",
        description="No description set",
        description_localizations={},
        dm_permission=True,
        name="base",
        name_localizations={},
        options=[
            {
                "description": "OwO!",
                "description_localizations": None,
                "name": "command",
                "name_localizations": None,
                "options": [],
                "type": 1,
            }
        ],
        type=1,
    )


def test_sub_command_with_option(fake_client):
    @fake_client.command()
    async def base(*args, **kwargs):
        pass

    @base.subcommand()
    @interactions.option("UwU nya~", name="OwO")
    async def command(ctx, owo: str = None):
        """OwO!"""

    assert base.full_data == dict(
        default_member_permissions="2147483648",
        description="No description set",
        description_localizations={},
        dm_permission=True,
        name="base",
        name_localizations={},
        options=[
            {
                "description": "OwO!",
                "description_localizations": None,
                "name": "command",
                "name_localizations": None,
                "options": [
                    {
                        "description": "UwU nya~",
                        "name": "OwO",
                        "required": False,
                        "type": interactions.OptionType.STRING,
                    }
                ],
                "type": 1,
            }
        ],
        type=1,
    )


def test_sub_command_group(fake_client):
    @fake_client.command()
    async def base(*args, **kwargs):
        pass

    @base.group()
    async def purr(*args, **kwargs):
        """nya~"""

    @purr.subcommand()
    async def sorry(ctx):
        """This developer has been furry-ized."""

    assert base.full_data == dict(
        default_member_permissions="2147483648",
        description="No description set",
        description_localizations={},
        dm_permission=True,
        name="base",
        name_localizations={},
        options=[
            {
                "description": "nya~",
                "description_localizations": None,
                "name": "purr",
                "name_localizations": None,
                "options": [
                    {
                        "description": "This developer has been furry-ized.",
                        "description_localizations": None,
                        "name": "sorry",
                        "name_localizations": None,
                        "options": [],
                        "type": 1,
                    }
                ],
                "type": 2,
            }
        ],
        type=1,
    )


def test_sub_command_group_with_options(fake_client):
    @fake_client.command()
    async def base(*args, **kwargs):
        pass

    @base.group()
    async def purr(*args, **kwargs):
        """nya~"""

    @purr.subcommand()
    @interactions.option("OwO nya~ purr")
    async def sorry(ctx, nya: int):
        """This developer has been furry-ized."""

    assert base.full_data == dict(
        default_member_permissions="2147483648",
        description="No description set",
        description_localizations={},
        dm_permission=True,
        name="base",
        name_localizations={},
        options=[
            {
                "description": "nya~",
                "description_localizations": None,
                "name": "purr",
                "name_localizations": None,
                "options": [
                    {
                        "description": "This developer has been furry-ized.",
                        "description_localizations": None,
                        "name": "sorry",
                        "name_localizations": None,
                        "options": [
                            {
                                "description": "OwO nya~ purr",
                                "name": "nya",
                                "required": True,
                                "type": interactions.OptionType.INTEGER,
                            }
                        ],
                        "type": 1,
                    }
                ],
                "type": 2,
            }
        ],
        type=1,
    )


def test_basic_invalid_command_failure(fake_client):
    @fake_client.command(name="HI")
    async def command(ctx):
        """Hello!"""

    with pytest.raises(interactions.LibraryException):
        fake_client._Client__resolve_commands()


def test_basic_command_with_invalid_option_failure(fake_client):
    @fake_client.command()
    @interactions.option("hi", name="HI")
    async def command(ctx, hi: str):
        """Hello!"""

    with pytest.raises(interactions.LibraryException):
        fake_client._Client__resolve_commands()


def test_invalid_sub_command_failure(fake_client):
    @fake_client.command()
    async def command(ctx):
        """Hello!"""

    @command.subcommand()
    async def SUBCOMMAND(ctx):  # noqa
        """Hi!"""

    with pytest.raises(interactions.LibraryException):
        fake_client._Client__resolve_commands()


def test_sub_command_with_invalid_option_failure(fake_client):
    @fake_client.command()
    async def command(ctx):
        """Hello!"""

    @command.subcommand()
    @interactions.option(name="HI")
    async def subcommand(ctx, hi: str):  # noqa
        """Hi!"""

    with pytest.raises(interactions.LibraryException):
        fake_client._Client__resolve_commands()


def test_invalid_sub_command_group_failure(fake_client):
    @fake_client.command()
    async def command(ctx):
        """Hello!"""

    @command.group()
    async def GROUP(ctx):  # noqa
        """Hi!"""

    @GROUP.subcommand()
    async def sub(ctx):
        """OwO!"""

    with pytest.raises(interactions.LibraryException):
        fake_client._Client__resolve_commands()


def test_invalid_sub_command_group_no_sub_cmd_failure(fake_client):
    @fake_client.command()
    async def command(ctx):
        """Hello!"""

    @command.group()
    async def group(ctx):
        """Hi!"""

    with pytest.raises(interactions.LibraryException):
        fake_client._Client__resolve_commands()


def test_sub_command_group_invalid_sub_cmd_failure(fake_client):
    @fake_client.command()
    async def command(ctx):
        """Hello!"""

    @command.group()
    async def group(ctx):
        """Hi!"""

    @group.subcommand()
    async def SUB(ctx):  # noqa
        """OwO!"""

    with pytest.raises(interactions.LibraryException):
        fake_client._Client__resolve_commands()


def test_sub_command_group_with_invalid_sub_cmd_option_failure(fake_client):
    @fake_client.command()
    async def command(ctx):
        """Hello!"""

    @command.group()
    async def group(ctx):
        """Hi!"""

    @group.subcommand()
    @interactions.option(name="HI")
    async def sub(ctx, hi: str):  # noqa
        """OwO!"""

    with pytest.raises(interactions.LibraryException):
        fake_client._Client__resolve_commands()
