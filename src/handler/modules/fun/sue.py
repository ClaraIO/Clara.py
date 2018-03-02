#!/usr/bin/env python3

"""A command that sues someone or something."""

import random
import re

from k3 import commands

systemrandom = random.SystemRandom()


@commands.cooldown(6, 12)
@commands.command()
async def sue(ctx, *args):
    """Sue somebody!

    Example usage:

    * sue
    * sue a person
    """
    target = " ".join(args)
    conjunctions = " because | for | over "
    parts = [part.strip() for part in re.split(conjunctions, target, 1, re.I)]
    if len(parts) > 1 and parts[1]:
        conjunction = re.search(conjunctions, target, re.I).group(0)
        target = parts[0]
        reason = conjunction + ctx.f.bold(parts[1])
    else:
        reason = ""
    if target:
        target = ctx.f.bold(" " + target)
    amount = ctx.f.bold("$" + str(systemrandom.randint(100, 1000000)))
    message = f"I-I'm going to sue{target} for {amount}{reason}! o.o"
    await ctx.send(message)
