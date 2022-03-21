interactions.py
===============

Easy, simple, scalable and modular: a library for interactions.

Where do I start?
~~~~~~~~~~~~~~~~~

Our documentation is divided into three main sections:

.. toctree::
    :maxdepth: 1

    quickstart.rst
    migration.rst
    api.rst

.. seealso::

    For documentation pertaining how to create 3rd party libraries/"extensions,"
    check out our howto on :ref:`3rd party development. <ext.gettingstarted:Developing a 3rd party.>`

    If you've come here but weren't able to get something working the way you intended,
    check out our :ref:`Frequently Asked Questions <faq:Frequently Asked Questions>` first.

What are we?
************

interactions.py is a Python library giving developers across Discord the ability to implement effective
solutions into their bots. Simply put, we're the best library out there to make slash commands, components
and the likes appear in the most elegant way possible.

This project is the accumulation of years of tested functionality all into one library for bot developers to
freely use. Since December 2020, we've been paving the road for developers to use interactions in their Python
Discord bots.

What can we do?
***************

interactions.py offers a magnitude of benefits worthy of use in a Discord bot. Such benefits include:

- **Dynamic object generation**: the flagship feature of our library, we dispatch objects of returned API data from the respective schema of various resources and other objects given by our REST and Gateway handlers.
- **Sane rate limiting**: protecting developers from being put in the timeout corner. A "sane" rate limit is a common requirement for libraries as bot developers' needs require pre-emptively avoiding a rate limit from the Discord API. We will check for a rate limit per HTTP route, bucket, major and non-major parameters; (e.g. HTTP request type ``GET``) and global request.
- **On-demand caching**: storing data when necessary. Our competitors' approach to caching relies on doing so during the initialization/pre-"ready" state of the client-facing connection to the API. This tends to lead towards excessive taxing on memory and high CPU calls. We will only cache data when absolutely necessary, and handle the garbage collection for you.
- **Simplified data**: making a better understanding out of what the Discord API gives you. Bot developers are regularly working with all forms of data in their applications, so understanding what you're using is important. We abstract all data returned into existing objects of their own where applicable as resources of the API's returned objects, as well as thoroughly documentation.
- **Dual-way decorator logic**: we allow for bot developers to make callbacks in two ways---dispatching an event (e.g. command/component coroutine methods) and registering a command. We simplify the workflow in creating and automating a bots' application commands with the Discord API.
- **API schema strictness**: an end to confusion with naming conventions. We will always follow the same naming style and nomenclature as the Discord API does, putting an end to misunderstandings with aliases and other undesired complications.
- **External software development kit**: giving power to bot developers. Our external SDK gives developers the freedom to creatively implement their own design choices into our library. (Check out :ref:`developing a 3rd party. <ext.gettingstarted:Developing a 3rd party.>` for more details.)

What is not offered?
********************

.. info::

    This list is currently incomplete.
    If there is something missing here, we welcome `pull requests!`_.

Advanced Search
===============

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _pull requests: https://github.com/interactions-py/library/blob/unstable/CONTRIBUTING.rst#new-to-contributing