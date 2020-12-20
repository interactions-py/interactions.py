discord-py-slash-command Events
================================
This page is about events of this extension.
These events can be registered to discord.py's listener or
``event`` decorator.

.. function:: on_slash_command(ctx)

    Called when slash command is triggered.

    :param ctx: SlashContext of the triggered command.
    :type ctx: :class:`.model.SlashContext`

.. function:: on_slash_command_error(ctx, ex)

    Called when slash command had an exception while the command was invoked.

    :param ctx: SlashContext of the triggered command.
    :type ctx: :class:`.model.SlashContext`
    :param ex: Exception that raised.
    :type ex: Exception

