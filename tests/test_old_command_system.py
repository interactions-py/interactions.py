# todo usr and msg cmds
# todo check everything as in new cmd system
# todo for helpers maybe replace _request?


import pytest

import interactions


def test_user_command(fake_client):
    @fake_client.command(name="Hello", type=interactions.ApplicationCommandType.USER)
    async def func(ctx):
        ...

    assert func.full_data == dict(
        default_member_permissions="2147483648",
        description="",
        description_localizations={},
        dm_permission=True,
        name="Hello",
        name_localizations={},
        options=[],
        type=2,
    )

    @fake_client.user_command(name="Hello")
    async def func2(ctx):
        ...

    assert func2.full_data == dict(
        default_member_permissions="2147483648",
        description="",
        description_localizations={},
        dm_permission=True,
        name="Hello",
        name_localizations={},
        options=[],
        type=2,
    )


def test_message_command(fake_client):
    @fake_client.command(name="Hello", type=interactions.ApplicationCommandType.MESSAGE)
    async def func(ctx):
        ...

    assert func.full_data == dict(
        default_member_permissions="2147483648",
        description="",
        description_localizations={},
        dm_permission=True,
        name="Hello",
        name_localizations={},
        options=[],
        type=3,
    )

    @fake_client.message_command(name="Hello")
    async def func2(ctx):
        ...

    assert func2.full_data == dict(
        default_member_permissions="2147483648",
        description="",
        description_localizations={},
        dm_permission=True,
        name="Hello",
        name_localizations={},
        options=[],
        type=3,
    )


def test_basic_command(fake_client):
    @fake_client.command(name="command", description="Hello!")
    async def command(ctx: interactions.CommandContext):
        pass

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


def test_basic_command_with_required_option(fake_client):
    @fake_client.command(
        name="command",
        description="Hello!",
        options=[
            interactions.Option(
                name="option", type=interactions.OptionType.STRING, description="hi", required=True
            )
        ],
    )
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


def test_basic_command_with_required_option_and_localisations(fake_client):
    @fake_client.command(
        name_localizations={interactions.Locale.GERMAN: "befehl"},
        description_localizations={interactions.Locale.GERMAN: "Hallo!"},
        name="command",
        description="Hello!",
        options=[
            interactions.Option(
                name="option",
                description="hi",
                type=interactions.OptionType.STRING,
                required=True,
                name_localizations={interactions.Locale.GERMAN: "option"},
                description_localizations={interactions.Locale.GERMAN: "Hi"},
            )
        ],
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


def test_basic_command_with_not_required_option(fake_client):
    @fake_client.command(
        name="command",
        description="hi!",
        options=[
            interactions.Option(
                name="option", description="hi", type=interactions.OptionType.STRING, required=False
            )
        ],
    )
    async def command(ctx, option: str = ""):
        """Hello!"""

    assert command.full_data == dict(
        default_member_permissions="2147483648",
        description="hi!",
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


def test_basic_command_with_connector_option(fake_client):
    @fake_client.command(
        name="command",
        description="hi!",
        options=[
            interactions.Option(
                name="hi",
                description="hi",
                converter="d",
                type=interactions.OptionType.USER,
                required=True,
            )
        ],
    )
    async def command(ctx, d: interactions.Member):
        """Hello!"""

    assert command.full_data == dict(
        default_member_permissions="2147483648",
        description="hi!",
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
    @fake_client.command(
        name="command", description="hi!", dm_permission=False, default_member_permissions=8
    )
    async def command(ctx):
        """Hello!"""

    assert command.full_data == dict(
        default_member_permissions="8",
        description="hi!",
        description_localizations={},
        dm_permission=False,
        name="command",
        name_localizations={},
        options=[],
        type=1,
    )


def test_basic_command_with_multiple_options(fake_client):
    @fake_client.command(
        name="command",
        description="hi!",
        options=[
            interactions.Option(
                name="name", description="hi", type=interactions.OptionType.STRING, required=True
            ),
            interactions.Option(
                name="number", description="hi", type=interactions.OptionType.INTEGER, required=True
            ),
            interactions.Option(
                name="person", description="hi", type=interactions.OptionType.USER, required=True
            ),
        ],
    )
    async def command(ctx, name: str, number: int, person: interactions.Member):
        """Hello!"""

    assert command.full_data == dict(
        default_member_permissions="2147483648",
        description="hi!",
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
    @fake_client.command(
        name="command",
        description="Hello!",
        options=[
            interactions.Option(
                name="option",
                description="hi",
                type=interactions.OptionType.STRING,
                required=False,
                choices=[
                    interactions.Choice(name="hi", value="hi"),
                    interactions.Choice(name="bye", value="bye"),
                ],
            )
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
    @fake_client.command(
        name="base",
        description="No description set",
        options=[
            interactions.Option(
                name="command", type=interactions.OptionType.SUB_COMMAND, description="OwO!"
            )
        ],
    )
    async def base(*args, **kwargs):
        pass

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
                "name": "command",
                "type": 1,
            }
        ],
        type=1,
    )


def test_sub_command_with_option(fake_client):
    @fake_client.command(
        name="base",
        description="No description set",
        options=[
            interactions.Option(
                name="command",
                type=interactions.OptionType.SUB_COMMAND,
                description="OwO!",
                options=[
                    interactions.Option(
                        name="OwO",
                        description="UwU nya~",
                        required=False,
                        type=interactions.OptionType.STRING,
                    )
                ],
            )
        ],
    )
    async def base(*args, **kwargs):
        pass

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
                "name": "command",
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
    @fake_client.command(
        name="base",
        description="No description set",
        options=[
            interactions.Option(
                name="purr",
                type=interactions.OptionType.SUB_COMMAND_GROUP,
                description="nya~",
                options=[
                    interactions.Option(
                        name="sorry",
                        description="This developer has been furry-ized.",
                        type=interactions.OptionType.SUB_COMMAND,
                        options=[],
                    )
                ],
            )
        ],
    )
    async def base(*args, **kwargs):
        pass

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
                "name": "purr",
                "options": [
                    {
                        "description": "This developer has been furry-ized.",
                        "name": "sorry",
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
    @fake_client.command(
        name="base",
        description="No description set",
        options=[
            interactions.Option(
                name="purr",
                type=interactions.OptionType.SUB_COMMAND_GROUP,
                description="nya~",
                options=[
                    interactions.Option(
                        name="sorry",
                        description="This developer has been furry-ized.",
                        type=interactions.OptionType.SUB_COMMAND,
                        options=[
                            interactions.Option(
                                description="OwO nya~ purr",
                                name="nya",
                                required=True,
                                type=interactions.OptionType.INTEGER,
                            )
                        ],
                    )
                ],
            )
        ],
    )
    async def base(*args, **kwargs):
        pass

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
                "name": "purr",
                "options": [
                    {
                        "description": "This developer has been furry-ized.",
                        "name": "sorry",
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


#
def test_basic_invalid_command_failure(fake_client):
    @fake_client.command(name="HI")
    async def command(ctx):
        ...

    with pytest.raises(interactions.LibraryException):
        fake_client._Client__resolve_commands()


def test_basic_command_with_invalid_option_failure(fake_client):
    @fake_client.command(
        name="command", description="hi", options=[interactions.Option(name="HI", type=4)]
    )
    async def command(ctx, hi: str):
        """Hello!"""

    with pytest.raises(interactions.LibraryException):
        fake_client._Client__resolve_commands()


def test_invalid_sub_command_failure(fake_client):
    @fake_client.command(
        **dict(
            default_member_permissions="2147483648",
            description="No description set",
            description_localizations={},
            dm_permission=True,
            name="base",
            name_localizations={},
            options=[
                {
                    "description": "nya~",
                    "name": "purr",
                    "options": [
                        {
                            "description": "This developer has been furry-ized.",
                            "name": "SORRY",
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
    )
    async def command(ctx):
        """Hello!"""

    with pytest.raises(interactions.LibraryException):
        fake_client._Client__resolve_commands()


def test_sub_command_with_invalid_option_failure(fake_client):
    @fake_client.command(
        **dict(
            default_member_permissions="2147483648",
            description="No description set",
            description_localizations={},
            dm_permission=True,
            name="base",
            name_localizations={},
            options=[
                {
                    "description": "nya~",
                    "name": "purr",
                    "options": [
                        {
                            "description": "This developer has been furry-ized.",
                            "name": "sorry",
                            "options": [
                                {
                                    "description": "OwO nya~ purr",
                                    "name": "NYA",
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
    )
    async def command(ctx):
        """Hello!"""

    with pytest.raises(interactions.LibraryException):
        fake_client._Client__resolve_commands()


def test_invalid_sub_command_group_failure(fake_client):
    @fake_client.command(
        **dict(
            default_member_permissions="2147483648",
            description="No description set",
            description_localizations={},
            dm_permission=True,
            name="base",
            name_localizations={},
            options=[
                {
                    "description": "nya~",
                    "name": "PURR",
                    "options": [
                        {
                            "description": "This developer has been furry-ized.",
                            "name": "sorry",
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
    )
    async def command(ctx):
        """Hello!"""

    with pytest.raises(interactions.LibraryException):
        fake_client._Client__resolve_commands()


#
def test_invalid_sub_command_group_no_sub_cmd_failure(fake_client):
    @fake_client.command(
        **dict(
            default_member_permissions="2147483648",
            description="No description set",
            description_localizations={},
            dm_permission=True,
            name="base",
            name_localizations={},
            options=[
                {
                    "description": "nya~",
                    "name": "purr",
                    "type": interactions.OptionType.SUB_COMMAND_GROUP,
                }
            ],
            type=1,
        )
    )
    async def command(ctx):
        """Hello!"""

    with pytest.raises(interactions.LibraryException):
        fake_client._Client__resolve_commands()
