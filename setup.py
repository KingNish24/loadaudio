from setuptools import setup, find_packages
import pathlib

def get_version() -> str:
    rel_path = "loadaudio/__init__.py"
    with open(rel_path, "r") as fp:
        for line in fp.read().splitlines():
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="loadaudio",
    version=get_version(),
    author="Nishith Jain",
    author_email="kingnish24@gmail.com",
    description="a python package to effortlessly load audio and convert audio to different formats.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KingNish24/loadaudio",  
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "setuptools",
        "pydub",
        "requests",
        "numpy",
        "wheel",
        "typing"
    ],
)