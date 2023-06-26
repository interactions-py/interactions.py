import itertools
from pathlib import Path

import tomli
from setuptools import find_packages, setup

with open("pyproject.toml", "rb") as f:
    pyproject = tomli.load(f)

extras_require = {
    "voice": ["PyNaCl>=1.5.0,<1.6"],
    "speedup": ["aiodns", "orjson", "Brotli", "faust-cchardet", "uvloop; sys_platform != 'win32'"],
    "sentry": ["sentry-sdk"],
    "jurigged": ["jurigged"],
    "console": ["aioconsole>=0.6.0"],
}
extras_require["all"] = list(itertools.chain.from_iterable(extras_require.values()))
extras_require["docs"] = extras_require["all"] + [
    "mkdocs-autorefs",
    "mkdocs-awesome-pages-plugin",
    "mkdocs-material",
    "mkdocstrings-python",
    "mkdocs-minify-plugin",
    "mkdocs-git-committers-plugin-2",
    "mkdocs-git-revision-date-localized-plugin",
    "griffe==0.25",
]
extras_require["tests"] = [
    "pytest",
    "pytest-asyncio",
    "pytest-cov",
    "python-dotenv",
    "typeguard",
]
extras_require["dev"] = extras_require["tests"] + extras_require["docs"] + ["pre-commit"]

setup(
    name="interactions.py",
    description=pyproject["tool"]["poetry"]["description"],
    long_description=(Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown",
    author="LordOfPolls",
    author_email="dev@lordofpolls.com",
    url="https://github.com/interactions-py/interactions.py",
    version=pyproject["tool"]["poetry"]["version"],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=(Path(__file__).parent / "requirements.txt").read_text().splitlines(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: AsyncIO",
        "Framework :: aiohttp",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Documentation",
        "Typing :: Typed",
    ],
    project_urls={
        "Discord": "https://discord.gg/KkgMBVuEkx",
        "Documentation": "https://naff-docs.readthedocs.io/en/latest/",  # TODO: replace
    },
    extras_require=extras_require,
)
