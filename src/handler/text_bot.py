#!/usr/bin/env python3

"""A basic command-line bot made using k3's command handler."""

import asyncio
import os
import sys

from k3 import commands

loop = asyncio.get_event_loop()
bot = commands.Bot(loop=loop, prefix="k3", logout=sys.exit)


async def send(message):
    """Here is a very basic send coroutine, for a text bot."""
    print(message)


async def main():
    """Main method called from a run_until_complete() or similar."""
    print(f"Enter commands here. Commands must start with {bot.prefix}")
    print(f"For help, use {bot.prefix} help.")
    while 1:
        message = input("> ")
        try:
            # Always perform an owner override, since this is just a command line bot.
            await bot.process(message, is_owner=True, callback_send=send)
        except Exception as error:
            print(error)

if __name__ == "__main__":
    # Automatically load all modules.
    for dirpath, dirnames, filenames in os.walk("modules"):
        for filename in filenames:
            if filename.endswith(".py"):
                fullpath = os.path.join(dirpath, filename).split(os.sep)
                module = ".".join(fullpath)[:-3]  # Eliminate the .py
                try:
                    bot.add_module(module, skip_duplicate_commands=True)
                except Exception as error:
                    print(f"Unable to load {module}: {error}")
    try:
        loop.run_until_complete(main())
    except Exception:
        loop.close()
