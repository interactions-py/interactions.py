Getting started.
================

Developing a 3rd party.
***********************

Getting started with making a 3rd party library is pretty hard. Most of the time,
you'll find yourself often checking the source code and directly making changes
to the library. We want to make a change to that, and additionally, make it easier
for developers to find creativity in the simplicity of our overengineered product.

.. caution::

    If you're not familiar with the source code of the library, you should
    probably read the documentation first.

    Basing your 3rd party libraries off of our ``unstable`` branch is a bad
    practice as this is regarded as our development branch. Breaking changes
    may become common, and as a result pose a risk in affecting your 3rd party.
    For this reason, we recommend you use the latest PyPI release or ``stable``
    branch.

Installing
**********

Installing the external framework is a rather trivial process. You do not need
to run any special installation on the library, as this comes built into our
main core. However, you will need to install the dependencies involved with
the library.

If you do not already have this library installed, you can do with this line
below:

.. code-block:: bash

    pip install -U discord-py-interactions

Creating the base.
******************

For every official 3rd party library of interactions.py, we have a "core" for it,
otherwise known as the base. This base is what we use to allow developers to easily
setup their project onto PyPI and build, as well as storing additional information
that bot developers can read off of for their bots.

This code shows a basic example for creating the base of a 3rd party:

.. code-block:: python

    from interactions.ext import Base, build, Version, VersionAuthor

    version = (
        Version(
            version="0.0.1",
            author=VersionAuthor(
                name="name",
                email="example@email.com",
            ),
        ),
    )
    __version__ = str(version)

    data: dict = {
        "name": "interactions-name_here",
        "description": "We do cool things!",
        "version": version
        "link": "https://example.com",
        "packages": ["interactions.ext.name_here"]
    }

    build(Base(**data))

This configures the base of the library in a rather simple manner: you give the name
and description of the 3rd party, as well as its own official version and link for
reference. This is all that is required to build the library. The rest of the field
that can be filled in are optional. You can look at the :ref:`Base class <ext.base:Core Model>`
for more information.

Defining a version.
*******************

As you may have noticed in the ``Base`` class, we have a ``Version`` class that helps
define the version of the 3rd party. This is required to be written in our class for numerous reasons:

- To help enforce consistency in the formatting of 3rd party versions.
- To allow for easy version comparison.
- Forced semantic versioning.

This class is our most advanced and complicated one due to the abundant nature in emphasising
a proper versioning system. We have a few options for versioning, and we have a few rules to follow.

1. Major, minor and patch versions **must** be declared as either their respective key-word arguments, or under the ``version`` kwarg.
2. The version should not be author-less. Every library has an author behind a version.
3. The version should not be a pre-release. Pre-releases are not supported by the official PyPI. To release as alpha or beta, use the ``extend_version()`` method.
4. A version cannot contain more than 1 main author. If you have multiple authors, you should label them as co-authors instead.
5. An alphanumeric version can only contain one instance of its own.

With these rules out of the way, let's look at a simple implementation of the ``Version`` class
alongside its brother, ``VersionAuthor`` for adding authors of a version:

.. code-block:: python

    from interactions.ext import Version, VersionAuthor

    version = Version(
        major=1,
        minor=2,
        patch=3,
        # author=VersionAuthor(name="BobDotCom"),
        authors=[
            VersionAuthor(name="BobDotCom"),
            VersionAuthor(name="fl0w", shared=True),
        ],
    )  # Version(version="1.2.3")
    version.extend_version(beta=1)  # Version(version="1.2.3-beta.1")

    print(version.author)  # <VersionAuthor object at 0x0000000>
    print(version.author.name)  # BobDotCom
    print([author.name for author in version.authors])  # ['BobDotCom', 'fl0w']
    print(version.is_alphanumeric)  # True

This code example can also show you the ways of retreiving information from a version. As
seen here, this is a highly versatile class. These following are the shown methods and
their purposes:

- The ``version`` attribute is the version string.
- The ``major`` attribute is the major version number, e.g. "x.0.0"
- The ``minor`` attribute is the minor version number, e.g. "0.x.0"
- The ``patch`` attribute is the patch version number, e.g. "0.0.x"
- The ``authors`` property method is a list of authors, regardless of if one is a co-author or not.
- The ``is_alphanumeric`` property method is a boolean that indicates if the version is alphanumeric.

Converting models from one to another.
**************************************

The term "conversion" is a gross exaggeration of what we're actually doing here. The problem
that we've found with bot developers cross-referencing from different libraries is that
their data models are simply different in design and structure. In order to combat against this,
we have decided to create a conversion tool that will allow us to convert between models. This
tool also allows for better comparison that will save the average developer many lines of code
from having to be written. This is a basic example of how we "convert" these models:

.. code-block:: python

    from interactions.ext import Converter

    ref: dict = {
        "hello": "world",
        "foo": "bar",
        "goodbye": "cruel world",
    }
    some_random_thing: dict = {
        "hi": "everyone",
        "foo": "bar",
        "spam": "eggs",
    }

    converted = Converter(ref, some_random_thing)
    print(converted.difference)  # {'hello': 'world', 'goodbye': 'cruel world'}
    print(converted.missing)  # {'hi': 'everyone', 'spam': 'eggs'}
    print(converted)  # <Converter object at 0x0000000>

What about errors?
******************

Don't worry---we've got you covered there. Each of our tools will raise special error exceptions that
you can listen to. Since this is a pretty self-explanitory subject, we recommend :ref:`reading the documentation <ext.error:Error Exceptions>`
on this.
