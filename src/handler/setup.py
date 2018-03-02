#!/usr/bin/env python3

from setuptools import setup

extras_require = {
    "http": ["aiohttp"],
    "full": ["aiohttp", "beautifulsoup4", "html2text"],
    "discord": ["aiohttp", "beautifulsoup4", "html2text", "discord.py"]
}

setup(name="k3",
      version="3.0.0a",
      description="A bot command handling framework in Python",
      license="MIT",
      packages=["k3"],
      zip_safe=False,
      extras_require=extras_require)
