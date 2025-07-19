from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent

setup(
    name = "curation",
    version = "1.0.1",
    author = "Joshua Rivera",
    author_email = "jriver44@gmail.com",
    description = "A CLI colleciton tracker with analytics.",
    long_description=(here / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/jriver44/collectory",
    packages=find_packages(exclude=["tests*", "api*"]),
    python_requires=">=3.8",
    install_requires = [
        "colorama",
        "tabulate",
        "flask",
        "ariadne",
    ],
    entry_points={
        "console_scripts": [
            "curation=collectory.collector:main",
        ],
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)