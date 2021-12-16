import re
from codecs import open
from os import path

from setuptools import find_packages, setup

PACKAGE_NAME = "interactions"
HERE = path.abspath(path.dirname(__file__))

with open("README.rst", "r", encoding="UTF-8") as f:
    README = f.read()
with open(path.join(HERE, PACKAGE_NAME, "base.py"), encoding="utf-8") as fp:
    VERSION = re.search('__version__ = "([^"]+)"', fp.read()).group(1)

extras = {
    "lint": ["black", "flake8", "isort"],
    "readthedocs": ["sphinx", "karma-sphinx-theme"],
}
extras["lint"] += extras["readthedocs"]
extras["dev"] = extras["lint"] + extras["readthedocs"]

requirements = open("requirements.txt").read().split("\n")[:-1]

setup(
    name="discord-py-interactions",
    version=VERSION,
    author="goverfl0w",
    author_email="james.discord.interactions@gmail.com",
    description="Easy, simple, scalable and modular: a Python API wrapper for interactions.",
    extras_require=extras,
    install_requires=requirements,
    license="MIT License",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/goverfl0w/discord-interactions",
    packages=find_packages(),
    python_requires=">=3.8.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
)
