#!/usr/bin/env python3

"""Commands that give the bot's opinions on things."""

import random

from k3 import commands

systemrandom = random.SystemRandom()


@commands.cooldown(6, 12)
@commands.command()
async def choose(ctx, *choices):
    """Randomly choose between one of various supplied things.

    Example usage:

    * choose x y z - Choose between x, y, and z.
    * choose x "y z" "a b" - Choose between x, y z, and a b.
    """
    if len(choices) <= 1:
        await ctx.send("Not enough choices given!")
        return
    elif len(set(choices)) == 1:
        await ctx.send("They're all the same, I can't choose!")
        return
    choice = systemrandom.choice(choices)
    await ctx.send(choice)
