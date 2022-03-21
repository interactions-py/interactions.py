.. currentmodule:: interactions

API Reference
=============

The Discord API is a vastly complex application programming interface. The goal of this page is to
thoroughly cover over all aspects of our client-facing implementation of the API to make better sense
of what's going on.

.. tip::

    Our documentation uses various symbols to add context to something. For example, a ``?`` on an attribute
    means that the attribute in question is always optional, and not "temporarily" optional. We recommend
    only looking at the attribute's typing for an idea of how it's parsed, not the final rendition of its value.

Bot Developing
**************

This section covers all of the documentation related to how we as the bot developer interact with connecting
and "talking" to the Discord API.

.. hint::

    If you're looking for coding things that only you should be concerned about,
    we highly recommend only looking at documentation lacking a warning, caution or
    danger admonition.

.. toctree::
    :maxdepth: 2
    
    client.rst
    context.rst

Internal development
********************

This section covers over the internal aspects of our library.

Handlers
~~~~~~~~

"Handlers" is our way of stating something that interacts with another thing on a technical level.

.. toctree::
    :maxdepth: 1

    api.http.rst
    api.gateway.rst
    
Data Models
~~~~~~~~~~~

"Data models" are a term in our vocabulary here at interactions.py to describe how we shape and show
data given from the API. Data is an ambigious term that can resemble information from the Gateway
packet stream, (e.g. events) HTTP request returns, or interfacing with library classes.

The most common form of a data model is a Python subclassed object.

.. toctree::
    :maxdepth: 1

    api.models.channel.rst
    api.models.flags.rst
    api.models.guild.rst
    api.models.gw.rst
    api.models.member.rst
    api.models.message.rst
    api.models.misc.rst
    api.models.presence.rst
    api.models.role.rst
    api.models.team.rst
    api.models.user.rst
