from discord import User

class IntegrationApplication:
    def __init__(self, state, data, bot=None):
        self._state = state
        self.id = int(data.get('id'))
        self.name = data.get('name')
        self.icon = data.get('icon')
        self.description = data.get('description')
        self.summary = data.get('summary')
        if bot is None:
            bot_data = data.get('bot')
            if bot_data is not None:
                self.bot = User(state=state, data=bot_data)
        else:
            self.bot = bot

    async def commands(self, guild=None):
        if guild is not None:
            data = await self._state.http.get_application_commands(self.id, guild.id)
        else:
            data = await self._state.http.get_application_commands(self.id)
        commands = []
        for command in data:
            commands.append(ApplicationCommand(data=command))
        return commands

class OptionType:
    sub_command = 1
    sub_command_group = 2
    string = 3
    integer = 4
    boolean = 5
    user = 6
    channel = 7
    role = 8