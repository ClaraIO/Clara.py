#!/usr/bin/env python3

"""Reaction image commands. Reads from a JSON."""

import json
import random

from k3 import commands

systemrandom = random.SystemRandom()

_globals = globals()

# This programmatically generates the reaction image commands.
with open("reactions.json") as fobject:
    data = json.load(fobject)

    for key in data:

        if (not isinstance(data[key], dict) or
                not isinstance(data[key].get("images"), list)):
            print(f"Skipping malformed command {key}.")
            continue

        aliases = data[key].get("aliases", [])

        help = f"{key.capitalize()}!"

        async def coro(ctx):
            await ctx.send(systemrandom.choice(data[ctx.command.name]["images"]))

        # Ew, gross.
        _globals[key] = commands.command(name=key, aliases=aliases, help=help)(coro)
        _globals[key].set_cooldown(6, 12)
