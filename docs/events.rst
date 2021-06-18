discord_slash Events
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

.. function:: on_component(ctx)

    Called when a component is triggered.

    :param ctx: ComponentContext of the triggered component.
    :type ctx: :class:`.model.ComponentContext`

.. function:: on_component_callback(ctx, callback)

    Called when a component callback is triggered.

    :param ctx: ComponentContext of the triggered component.
    :type ctx: :class:`.model.ComponentContext`
    :param callback: triggered ComponentCallbackObject
    :type callback: :class:`.model.ComponentCallbackObject`

.. function:: on_component_callback_error(ctx, ex)

    Called when component callback had an exception while the callback was invoked.

    :param ctx: Context of the callback.
    :type ctx: :class:`.model.ComponentContext`
    :param ex: Exception from the command invoke.
    :type ex: Exception