import re
from codecs import open
from os import path

from setuptools import find_packages, setup

PACKAGE_NAME = "discord_slash"
HERE = path.abspath(path.dirname(__file__))

with open("README.md", "r", encoding="UTF-8") as f:
    README = f.read()
with open(path.join(HERE, PACKAGE_NAME, "const.py"), encoding="utf-8") as fp:
    VERSION = re.search('__version__ = "([^"]+)"', fp.read()).group(1)

extras = {
    "lint": ["black", "flake8", "isort"],
    "readthedocs": ["sphinx", "sphinx-rtd-theme"],
}
extras["lint"] += extras["readthedocs"]
extras["dev"] = extras["lint"] + extras["readthedocs"]

setup(
    name="discord-py-slash-command",
    version=VERSION,
    author="LordOfPolls",
    author_email="ddavidallen13@gmail.com",
    description="A simple interaction handler for discord.py.",
    extras_require=extras,
    install_requires=["discord.py", "aiohttp"],
    license="MIT License",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/discord-py-slash-commands/discord-py-interactions",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
)
