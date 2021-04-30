import re
import setuptools
from codecs import open
from os import path

PACKAGE_NAME = "discord_slash"
HERE = path.abspath(path.dirname(__file__))

with open("README.md", "r", encoding="UTF-8") as f:
    long_description = f.read()
with open(path.join(HERE, PACKAGE_NAME, "const.py"), encoding="utf-8") as fp:
    VERSION = re.search('__version__ = "([^"]+)"', fp.read()).group(1)

setuptools.setup(
    name="discord-py-slash-command",
    version=VERSION,
    author="eunwoo1104",
    author_email="sions04@naver.com",
    description="A simple discord slash command handler for discord.py.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eunwoo1104/discord-py-slash-command",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3"
    ]
)
