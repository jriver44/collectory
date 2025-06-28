import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name="curation",
    version="1.0.0",
    author="Joshua Rivera",
    author_email="jriver44@gmail.com",
    description="A CLI collection tracker with analytics.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jriver44/collectory",
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "colorama",
        "tabulate",
    ],
    entry_points={
        "console_scripts": [
            "curation=collectory.collector:main"
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)