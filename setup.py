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


def read_requirements(filename):
    with open(filename, "r", encoding="utf-8") as fp:
        return fp.read().strip().splitlines()


extras = {
    "lint": read_requirements("requirements-lint.txt"),
    "readthedocs": read_requirements("requirements-docs.txt"),
}
extras["dev"] = extras["lint"] + extras["readthedocs"]
requirements = read_requirements("requirements.txt")

setup(
    name="discord-py-interactions",
    version=VERSION,
    author="goverfl0w",
    author_email="james.discord.interactions@gmail.com",
    description="Easy, simple, scalable and modular: a Python API wrapper for interactions.",
    extras_require=extras,
    install_requires=requirements,
    license="GPL-3.0 License",
    long_description=README,
    long_description_content_type="text/x-rst",
    url="https://github.com/interactions-py/library",
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
