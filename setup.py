import setuptools

with open("README.md", "r", encoding="UTF-8") as f:
    long_description = f.read()

setuptools.setup(
    name="discord-py-slash-command",
    version="1.0.9",
    author="eunwoo1104",
    author_email="sions04@naver.com",
    description="Simple Discord Slash Command extension for discord.py.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eunwoo1104/discord-py-slash-command",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3"
    ]
)
